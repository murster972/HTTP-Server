#!/usr/bin/env python3
import os
import re
import sys
import socket
import base64
import zlib
from threading import Thread
from status_codes import ErrorStatusCodes

#NOTE: Font files are sending but are not being decoded by browser
#TODO: Fix this^ shit
#      The problem may be with the font being in base64, try compressing
#      with gzip first
#NOTE: Server is someone sending the reply of the clients last request back to its self
#NOTE: ^This is meant to happen after every response sent by tehs server the client send back a response
#TODO: Check that this response(^see above) is recived from the client and if error try resending the response

class HTTPServer:
    clients = {}
    BUFF_SIZE = 2048
    #root_dir = "TestWebsite"
    root_dir = "/home/murster972/Documents/programming/python/HTTP Server/TestWebsite"
    server_name = "PythonHTTPServer"
    content_types = {}
    binary_files = []
    text_files = []

    def __init__(self):
        try:
            #server_IP, server_port = input("Server IP: "), 443
            server_IP, server_port = "127.0.0.1", 80
        except ValueError:
            print("[-] Invalid sever IP address or port number.")
            sys.exit(-1)

        self.get_content_types()

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((server_IP, server_port))
        self.server_sock.listen(5)

        print("[*] Server online at: {}:{}".format(server_IP, server_port))

        #Listens for clients
        try:
            while True:
                #TODO: Use TLS to connect to clients
                client_sock, client_addr = self.server_sock.accept()
                new_client = Thread(target=ClientHandler, args=[client_sock, client_addr], daemon=True)
                new_client.start()
        except (KeyboardInterrupt):
            pass
        finally:
            self.server_sock.close()
            print("[*] Server closed")

    def get_content_types(self):
        f = open("content_types.txt", "r")
        data = [i.replace("\n", "") for i in f.readlines() if i and i[0] != "#" and i != "\n"]
        f.close()

        for i in data:
            t = i.split("::")
            t1 = t[1].split(",")

            if t[0].split("/")[0] == "text": HTTPServer.text_files += t1
            else:  HTTPServer.binary_files += t1

            for i in t1: HTTPServer.content_types[i] = t[0]

    'Translates any unicode chars to ascii in uri, currently only supports UTF-8'
    def uri_decoder(self, u):
        new_u = ""
        l_u = len(u)

        valid_chars = [chr(i) for i in range(32, 127)]

        i = 0
        while i < l_u:
            if u[i] == "%":
                if i + 2 > l_u: return -1
                d = chr(int(u[i+1:i+3], 16))
                if d not in valid_chars: return -1
                new_u += d
                i += 3
            else:
                new_u += u[i]
                i += 1

        return new_u

    'Validates uri, checks invalid chars, converts uncidoe to ascii and removes backwards traversal attempts'
    def validate_uri(self, u):
        #checks for invalid characters
        #r_exp = r"[abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_\-.\/%\\]"
        r_exp = r"[a-zA-Z0-9_\-.\/%\\]"
        uri = re.sub(r_exp, "", u)

        if uri: return -1
        else: uri = u

        #converts any unicode to ascii
        uri = self.uri_decoder(uri)

        #removes any attempt of backwards traversal
        #TODO: Test this with attacks, and improve
        uri = uri.replace("../", "")

        root_dir = HTTPServer.root_dir
        root_dir += "/" if uri[0] != "/" else ""

        return "{}{}".format(root_dir, uri)

class ClientHandler(HTTPServer):
    def __init__(self, sock, addr):
        HTTPServer.clients[sock] = addr

        self.req_headers = {}

        try:
            while True:
                #recieves client requets
                req = sock.recv(HTTPServer.BUFF_SIZE).decode()
                split_req = self.split_request(req)
                connect_header = "closed" if "connecion" not in split_req[3] else split_req[3]["connection"]

                split_req[3]["connection"] = connect_header

                resp = self.handle_request(split_req)

                sock.send(resp.encode())

                if connect_header == "closed": break

        except ConnectionResetError:
            print("[*] Client closed connection")
        finally:
            sock.close()

    def handle_request(self, r):
        method, uri, http_ver, req_headers, body = tuple(r)
        #print(method, uri, http_ver, self.req_headers, body)

        uri = "/index.html" if uri == "/" or uri == "\\" else uri

        if method == "GET" or method == "HEAD":
            try:
                uri = self.validate_uri(uri)
                if uri == -1: raise HTTPBadRequest()

                ext = uri.split(".")
                ext = "text" if len(uri) < 2 else ext[-1].lower()

                #BUG: Binary data is not being sent corretly
                read_opt = "rb" if ext in HTTPServer.binary_files else "r"

                f = open(uri, read_opt)
                body = f.read()
                f.close()

                content_len = "Content-Length: {}".format(len(body))

                content_type = "text" if ext not in HTTPServer.content_types else HTTPServer.content_types[ext]
                content_type = "Content-Type: " + content_type

                #connection = "Connection: " + req_headers["connection"].title()
                connection = "Connection: Keep-Alive"

                #NOTE: Binary data is being read as a string instead of bytes by the client
                #TODO: Find the correct way to send binary data
                if method == "GET" and read_opt == "rb":
                    pass

                elif method == "HEAD":
                    body = ""

                return self.gen_response("HTTP/1.1 200 OK", headers=[content_type, content_len, connection], body=body)


            except FileNotFoundError:
                r = ErrorStatusCodes.get_status_code_page(404)
            except PermissionError:
                r = ErrorStatusCodes.get_status_code_page(405)
            except HTTPBadRequest:
                r = ErrorStatusCodes.get_status_code_page(400)
            except UnicodeDecodeError:
                r = ErrorStatusCodes.get_status_code_page(500)

        else:
            r = ErrorStatusCodes.get_status_code_page(405)

        #elif method == "POST":
        #    pass
        #elif method == "PUT":
        #    pass
        #elif method == "DELETE":
        #    pass
        #elif method == "CONNECT":
        #    pass
        #elif method == "OPTIONS":
        #    pass
        #elif  method == "TRACE":
        #    pass


        return self.gen_response(r[0], r[1], r[2])

    ' Generates HTTP Response '
    def gen_response(self, status_line, headers=[], body=""):
        resp = "{}\r\n".format(status_line)
        for i in headers: resp += str(i) + "\r\n"

        print(resp)

        resp += "\r\n{}".format(body)

        return resp

    'Splits request into, status line, uri, http protocol, headers and body'
    def split_request(self, r):
        req = r.split("\r\n")
        method, uri, http_ver = tuple(req[0].split())
        method = method.upper()

        method = method.upper()
        headers = {}

        i = 1
        while req[i]:
            h = req[i].split(": ")
            headers[h[0].lower()] = h[1].lower()
            i += 1

        body = req[i + 1:]

        return [method, uri, http_ver, headers, body]

class HTTPBadRequest(Exception): pass

if __name__ == '__main__':
    HTTPServer()

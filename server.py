#!/usr/bin/env python3
import os
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

class HTTPServer:
    clients = {}
    BUFF_SIZE = 2048
    root_dir = "TestWebsite"
    server_name = "PythonHTTPServer"
    content_types = {}
    binary_files = []
    text_files = []

    def __init__(self):
        try:
            #server_IP, server_port = input("Server IP: "), 443
            server_IP, server_port = "", 80
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

    def get_encoding(self):
        pass

class ClientHandler(HTTPServer):
    def __init__(self, sock, addr):
        HTTPServer.clients[sock] = addr

        self.req_headers = {}

        try:
            while True:
                #recieves client requets
                req = sock.recv(HTTPServer.BUFF_SIZE).decode()

                resp = self.handle_request(req)
                if not resp:
                    break

                #req_response = self.handle_request(req).encode()
                #sends result of Processed request to client
                sock.send(resp.encode())

        except ConnectionResetError:
            print("[*] Client closed connection")
        finally:
            sock.close()

    def handle_request(self, r):
        req = r.split("\r\n")
        method, uri, http_ver = tuple(req[0].split())

        #TODO: Ensure URI cannot be used to back track through directories
        uri = uri.replace("../", "")
        uri = uri if uri != "/" else "index.html"

        method = method.upper()
        headers = {}

        i = 1
        while req[i]:
            h = req[i].split(": ")
            headers[h[0]] = h[1]
            i += 1

        self.req_headers = headers

        body = req[i + 1:]

        if method == "GET" or method == "HEAD":
            try:
                if uri[0] == "/": uri = uri[1:]

                ext = uri.split(".")
                #changes any unknown or invalid ext to txt
                ext = "txt" if len(ext) == 0 or not ext[-1] else ext[-1]


                #NOTE: Doesnt take into account file ext not being in text or binary files,
                #      i.e. files not supported by server
                r_opt = "r" if ext in HTTPServer.text_files else "rb"

                f = open("{}/{}".format(HTTPServer.root_dir, uri), r_opt)

                #NOTE: Problem will occur as different binary files use different encoding
                #TODO: Find way to detect encoding
                f_data = f.read()
                headers = []

                if r_opt == "rb":
                    #NOTE: Trying to figure out how to compress font and send
                    #f_data = base64.b64encode(f_data)
                    f_data = zlib.compress(f_data)

                    #f_data = base64.b64encode(f_data)

                    #NOTE: Does not check if client accepts gzip encoding yet

                    #NOTE: Content-Encoding header causing font to fail
                    #headers.append("Content-Encoding: deflate")
                    headers.append("Accept-Ranges: bytes")
                    headers.append("Vary: Accept-Encoding")
                    #f_data = str(f_data)[2:-1]

                f.close()

                content_length = len(f_data)
                #f_data = f_data if r_opt == "r" else str(f_data)[2:-1]

                #NOTE: ONLY FOR TESTING PURPOSES
                if ext not in HTTPServer.content_types: ext = "txt"
                content_type = "content-type: {}".format(HTTPServer.content_types[ext])
                content_length = "content-length: {}".format(content_length)
                connect = "Connection: {}".format("Keep-alive" if self.req_headers["Connection"] == "keep-alive" else "Closed")
                connect = "Connection: Closed"
                headers += [content_type, content_length, connect]

                #TODO: Change so http ver isnt hard coded
                return self.gen_response("HTTP/1.1 200 OK", headers, f_data)

            except FileNotFoundError:
                r = ErrorStatusCodes.gen_status_code_page(404)
                return self.gen_response(r[0], r[1], r[2])
            #except (PermissionError, UnicodeDecodeError):
            except (PermissionError):
                r = HTTPStatusCodes.gen_status_code_page(403)
                return self.gen_response(r[0], r[1], r[2])

        elif method == "POST":
            pass
        elif method == "PUT":
            pass
        elif method == "DELETE":
            pass
        elif method == "CONNECT":
            pass
        elif method == "OPTIONS":
            pass
        elif  method == "TRACE":
            pass
        else:
            print("SEND ERROR STATING INVALID STATUS METHOD")

    ' Generates HTTP Response '
    def gen_response(self, status_line, headers=[], body=""):
        resp = "{}\r\n".format(status_line)
        for i in headers: resp += str(i) + "\r\n"

        print(resp)

        resp += "\r\n{}".format(body)

        return resp

if __name__ == '__main__':
    HTTPServer()

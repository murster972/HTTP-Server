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

        #converts any unicode to ascii

        #removes any attempt of backwards traversal
        pass

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

                resp = self.handle_request(split_req)

                sock.send(resp.encode())

                if connect_header == "closed": break

        except ConnectionResetError:
            print("[*] Client closed connection")
        finally:
            sock.close()

    def handle_request(self, r):
        method, uri, http_ver, self.req_headers, body = tuple(r)

        if method == "get" or method == "head":
            uri = HTTPServer.is_valid_uri()

            if uri == -1:
                r = status_codes.ErrorStatusCodes(400)
                return self.gen_response(r[0], r[1], r[2])


        """elif method == "post":
            pass
        elif method == "put":
            pass
        elif method == "delete":
            pass
        elif method == "connect":
            pass
        elif method == "options":
            pass
        elif  method == "trace":
            pass""""

        else:
            r = status_codes.ErrorStatusCodes(405)
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
        headers = {}

        i = 1
        while req[i]:
            h = req[i].split(": ")
            headers[h[0].lower()] = h[1].lower()
            i += 1

        body = req[i + 1:]

        return [method, uri, http_ver, headers, body]

if __name__ == '__main__':
    HTTPServer()

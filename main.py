#!/usr/bin/env python3
import os
import sys
import socket
import headers
import threading
from datetime import datetime

#BUG: Server only sending one file, e.g. sends index.html, but not test.css,
#     doesn't even receive the request for any other files after first request

class HTTPServer:
    '''HTTP server, clients connect make requests and HTTP server responds'''
    buff_size = 2048
    client_threads = []
    server_name = "PythonWebServer/0.0"
    root_dir = "TestWebsite"

    def __init__(self):
        server_addr = ("127.0.0.1", 80)
        #server_addr = ("192.168.10.1", 80)
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(server_addr)
            self.server.listen(5)

            print("[*] Server Listening at the address: {}".format(server_addr))

            self.buff_size = 2048

            while True:
                print("[*] Listening for clients")
                client_sock, client_addr = self.server.accept()
                print("[+] Client connected")
                #HTTPClient(client_sock, client_addr)
                client_thread = threading.Thread(target=HTTPClient, args=[client_sock, client_addr])
                client_thread.start()

        except KeyboardInterrupt:
            print("[*] Closing Server")

        except Exception as e:
            print("[-] The following error has occured and caused the server to stop: {}".format(e))
            sys.exit(1)

        finally:
            self.server.close()
            print("[*] Server Closed")

class HTTPClient(HTTPServer):
    '''Represents a client that has connected to the HTTP server'''
    def __init__(self, client_sock, client_addr):
        self.client_addr = client_addr
        self.client_sock = client_sock

        request = self.client_sock.recv(HTTPServer.buff_size).decode("utf-8")
        print(request)
        self.request_dict = {}
        self.read_request(request)
        response = self.create_response()
        print(response)

        self.client_sock.send(response.encode("utf-8"))
        self.client_sock.close()
        print("end")

    def create_response(self):
        '''Creates response for client based on contents of client request'''
        #TODO - Accept every method type, currently only accepts GET and HEAD
        #TODO - Workout "Content-type" header, right now its hardcoded to "text/html", "text/javascript" and "text/css"
        #TODO - Check that the "Content-type" of the file requested is part of the clients "Accepted-types" head
        method = self.request_dict["status_line"]["method"]

        if method == "GET" or method == "HEAD":
            try:
                uri = self.request_dict["status_line"]["URI"]
                uri = uri if uri != "/" else "/index.html"

                ext = uri.split(".")[::-1][0]
                content_type = ""
                if ext == "html": content_type = "text/html"
                elif ext == "js": content_type = "text/javascript"
                elif ext == "css": content_type = "text/css"

                f = open("{}{}".format(HTTPServer.root_dir, uri), "r").read()
                body = f if method == "GET" else ""
                resp = "HTTP/1.1 200 OK\r\nDate: {}\r\nServer: {}\r\nContent-Length: {}\r\n"\
                       "Content-type: {}\r\nConnection: Closed\r\n\r\n{}".format(datetime.now(), HTTPServer.server_name, len(f), content_type, body)

            except IOError:
                f = open("status_pages/404.html", "r").read()
                resp = "HTTP/1.1 404 Not Found\r\nDate: {}\r\nServer: PythonWebServer/0.0\r\nContent-Length: {}\r\n"\
                       "Content-type: text/html\r\nConnection: Closed\r\n\r\n{}".format(str(datetime.now()), len(f), f)
        else:
            f = open("status_pages/501.html", "r").read()
            resp = "HTTP/1.1 501 Not Implemented\r\nDate: {}\r\nServer: PythonWebServer/0.0\r\nContent-Length: {}\r\n"\
                   "Content-type: text/html\r\nConnection: Closed\r\n\r\n{}".format(str(datetime.now()), len(f), f)
        return resp

    def read_request(self, req):
        '''reads resuest, gets status line(method, uri), headers, and body'''
        try:
            r = req.split("\r\n")
            status_line = r[0].split(" ")
            self.request_dict["status_line"] = {"method": status_line[0], "URI": status_line[1], "protocol": status_line[2]}
            self.request_dict["headers"] = {}

            i = 1
            while r[i]:
                h = r[i].split(": ")
                self.request_dict["headers"][h[0]] = h[1]
                i += 1

            self.request_dict["body"] = [r[i + 1:]]
        except IndexError:
            self.request_dict = False

if __name__ == '__main__':
    HTTPServer()

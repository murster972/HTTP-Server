#!/usr/bin/env python3
import os
import sys
import socket
import base64
import headers
import threading
from datetime import datetime
from error_status_codes import StatusCodeErrors

#NOTE: This is - for some unknown reason - no longer a bug, it seems to have
#      fixed its self
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

    def create_response(self):
        '''Creates response for client based on contents of client request'''
        #TODO - Accept every method type, currently only accepts GET and HEAD
        #TODO - Workout "Content-type" header, right now its hardcoded to "text/html", "text/javascript" and "text/css"
        #TODO - Check that the "Content-type" of the file requested is part of the clients "Accepted-types" head

        #returns error if request dict is empty
        if not self.request_dict:
            return StatusCodeErrors.get_response(400, HTTPServer.server_name)

        method = self.request_dict["status_line"]["method"]
        error = 0

        if method == "GET" or method == "HEAD":
            try:
                uri = self.request_dict["status_line"]["URI"]
                uri = uri if uri != "/" else "/index.html"

                ext = uri.split(".")[::-1][0]
                if ext == "html": content_type = "text/html"
                elif ext == "js": content_type = "text/javascript"
                elif ext == "css": content_type = "text/css"
                elif ext == "otf": content_type = "application/font-woff2"

                #BUG: Doesn't return correct "content-type", i.e for css returns
                #     text/plain instead of text/css
                #m = mimetypes.MimeTypes()
                #url = request.pathname2url("{}{}".format(HTTPServer.root_dir, uri))
                #content_type, tmp = m.guess_type(url)

                #BUG: Any file thats not "utf-8" encoding cant be read correctly
                #print("{}{}".format(HTTPServer.root_dir, uri))
                try:
                    f = open("{}{}".format(HTTPServer.root_dir, uri), "r").read()
                except UnicodeDecodeError:
                    f = open("{}{}".format(HTTPServer.root_dir, uri), "rb").read()
                    #f = base64.b64encode(open("{}{}".format(HTTPServer.root_dir, uri), "rb").read())
                    #f = b'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'
                body = f if method == "GET" else ""
                resp = "HTTP/1.1 200 OK\r\nDate: {}\r\nServer: {}\r\nContent-Length: {}\r\n"\
                       "Content-type: {}\r\nConnection: Closed\r\n\r\n{}".format(datetime.now(), HTTPServer.server_name, len(f), content_type, body)

            except IOError:
                error = 404
        else:
            error = 405

        return resp if not error else StatusCodeErrors.get_response(error, HTTPServer.server_name)

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

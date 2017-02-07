#!/usr/bin/env python3
from datetime import datetime

class StatusCodeErrors:
    client_msg = ["400 Bad Request", "401 Unauthorized", "402 Payment Required", "403 Forbidden", "404 Not Found",\
                  "405 Method Not Allowed", "406 Not Acceptable", "407 Proxy Authentication Required", "408 Request Timeout",\
                  "409 Conflict", "410 Gone", "411 Length Required", "412 Precondition Failed", "413 Request Entity Too Large",\
                  "414 Request-url Too Long", "415 Unsupported Media Type", "416 Requested Range Not Satisfiable", "417 Expectation Failed"]

    server_msg = ["500 Internal Server Error", "501 Not Implemented", "502 Bad Gateway", "503 Service Unavailable", "504 Gateway Timeout",\
                  "505 HTTP Version Not Supported"]

    status_pages_dir = "status_pages"

    ''' Generates responses for error status codes '''
    def get_response(status_code, server_name):
        server_name = server_name.replace(" ", "").replace(":", "")
        if not isinstance(status_code, int):
             self.invalid_status_code("Status code must also be passed as an integer")
        str_status_code = str(status_code)
        valid = 0

        if str_status_code[0] == "4" and (status_code >= 400 and status_code <= 417):
            valid = 1
        elif str_status_code[0] == "5" and (status_code >= 500 and status_code <= 505):
            valid = 1

        if valid == 0: self.invalid_status_code()

        #e.g. client[404] = ["404 Page Not Found", "404.html"]
        #BUG: pages and error codes are being mixed, e.g. 404 Not found is being paired with 418.html
        #     may have something to do with the fact a dict keys do not stay in order
        client = {i:[StatusCodeErrors.client_msg[400 - i], str(i) + ".html"] for i in range(400, 418)}
        server = {i:[StatusCodeErrors.server_msg[500 - i], str(i) + ".html"] for i in range(500, 506)}
        client_server = {**client, **server}
        print(client_server)

        page = open("{}/{}".format(StatusCodeErrors.status_pages_dir, client_server[status_code][1]), "r").read()
        return "HTTP/1.1 {}\r\n"\
               "Date: {}\r\n"\
               "Server Name: {}\r\n"\
               "Content-Length: {}\r\n"\
               "Content-type: text/html\r\n\r\n"\
               "{}".format(client_server[status_code][0], datetime.now(), server_name, len(page), page)

    def invalid_status_code(self, msg=""):
        raise InvalidStatusCodeError("Status code must be client (400 - 417) or server (500 - 505) error status code. {}".format(msg))

class InvalidStatusCodeError(Exception):
    pass

if __name__ == '__main__':
    print(StatusCodeErrors.get_response(404, "PythonWebServer"))

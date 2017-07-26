#!/usr/bin/env python3

class ErrorStatusCodes:
    status_codes = {400: ["Bad Request", "The server did not understand the request."], 401: ["Unauthorized", "The requested page needs a username and a password."],
                    402: ["Payment Required", "You can not use this code yet."], 403: ["Forbidden", "Access is forbidden to the requested page."],
                    404: ["Not Found", "The server can not find the requested page."], 405: ["Method Not Allowed", "The method specified in the request is not allowed."],
                    406: ["Not Acceptable", "The server can only generate a response that is not accepted by the client."],
                    407: ["Proxy Authentication Required", "You must authenticate with a proxy server before this request can be served."],
                    408: ["Request Timeout", "The request took longer than the server was prepared to wait."],
                    409: ["Conflict", "The request could not be completed because of a conflict."], 410: ["Gone", "The requested page is no longer available."],
                    411: ["Length Required", "The 'Content-Length' is not defined. The server will not accept the request without it."],
                    412: ["Precondition Failed", "The pre condition given in the request evaluated to false by the server."],
                    413: ["Request Entity Too Large", "The server will not accept the request, because the request entity is too large."],
                    414: ["Request-url Too Long", "The server will not accept the request, because the url is too long. Occurs when you convert a 'post' request to a 'get' request with a long query information ."],
                    415: ["Unsupported Media Type", "The server will not accept the request, because the mediatype is not supported ."],
                    416: ["Requested Range Not Satisfiable", "The requested byte range is not available and is out of bounds."],
                    417: ["Expectation Failed", "The expectation given in an Expect request-header field could not be met by this server."],
                    500: ["Internal Server Error", "The request was not completed. The server met an unexpected condition."],
                    501: ["Not Implemented", "The request was not completed. The server did not support the functionality required."],
                    502: ["Bad Gateway", "The request was not completed. The server received an invalid response from the upstream server."],
                    503: ["Service Unavailable", "The request was not completed. The server is temporarily overloading or down."],
                    504: ["Gateway Timeout", "The gateway has timed out."], 505: ["HTTP Version Not Supported", "The server does not support the 'http protocol' version."]}

    'Returns status line, headers and body for an error status code'
    def get_status_code_page(status_code):
        if type(status_code) is not int:
            raise Exception("Invalid Status Code.")

        if int(status_code) not in ErrorStatusCodes.status_codes:
            raise Exception("Invalid Status Code. Unable to find the status code: {}".format(status_code))

        f = open("status_pages/{}.html".format(status_code))
        body = f.read()
        f.close()

        status_line = "HTTP/1.1 {} {}".format(status_code,  ErrorStatusCodes.status_codes[status_code][0])
        headers = ["Connection: Closed", "Content-Length: {}".format(len(body)), "Content-Type: text/html"]

        return [status_line, headers, body]

    'Generates HTML documents for each error status code'
    def gen_status_code_page():
        codes = [i for i in range(400, 418)]
        codes += [i for i in range(500, 506)]

        for c in codes:
            with open("status_pages/{}.html".format(c), "w") as f:
                title, descr = tuple(ErrorStatusCodes.status_codes[c])
                f.write("<html><head><title>{}</title></head><body><h1>{}</h1><h2>{}</h2></body></html>".format(title, title, descr))

if __name__ == '__main__':
    ErrorStatusCodes.gen_status_code_page()

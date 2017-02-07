#!/usr/bin/env python3
from error_status_codes import StatusCodeErrors

def main():
    ''' Generates html docs for status codes, 400-417 and 500-505 '''
    for j in range(400, 418):
        i = j - 400
        f = open("{}/{}.html".format(StatusCodeErrors.status_pages_dir, j), "w")
        f.write("<!DOCTYPE><html><head><title>Error {}</title></head><body><h1>Error on client side, Error {}</h1></body></html>".format(StatusCodeErrors.client_msg[i], StatusCodeErrors.client_msg[i]))

    for j in range(500, 506):
        i = j - 500
        f = open("{}/{}.html".format(StatusCodeErrors.status_pages_dir, j), "w")
        f.write("<!DOCTYPE><html><head><title></title></head><body><h1>Error on server side, Error {}</h1></body></html>".format(StatusCodeErrors.server_msg[i], StatusCodeErrors.server_msg[i]))

if __name__ == '__main__':
    main()

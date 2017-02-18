#!/usr/bin/env python3
from error_status_codes import StatusCodeErrors

def main():
    ''' Generates html docs for status codes, 400-417 and 500-505 '''
    for i in StatusCodeErrors.client_msg + StatusCodeErrors.server_msg:
        status_code = i[:3]
        f = open("{}/{}.html".format(StatusCodeErrors.status_pages_dir, status_code), "w")
        f.write("<!DOCTYPE><html><head><title>Error {}</title></head><body><h1>Error on client side, Error {}</h1></body></html>".format(status_code, i))
        f.close()

if __name__ == '__main__':
    main()

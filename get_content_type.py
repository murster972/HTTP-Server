#!/usr/bin/env python3
import os
import mimetypes
from urllib import request

''' gets file mime type for "Content-type" header '''
def get_content_type(fname):
    m = mimetypes.MimeTypes()
    url = request.pathname2url(fname)
    t = m.guess_type(url)
    print(t)

if __name__ == '__main__':
    get_content_type("Quicksand-Regular.otf")

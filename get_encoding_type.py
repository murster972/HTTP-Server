#!/usr/bin/env python3
import os

''' Gets the encoding type of a file, so that it can be read '''
def get_encoding_type(fname):
    encoding_types = ["ASCII", "UTF-8", "UTF-16", "UTF-32", "Big5", "GB2312",\
                      "HZ-GB-2312", "EUC-JP", "SHIFT_JIS", "ISO-2022-JP",\
                      "EUC-KR", "ISO-2022-KR", "KOI8-R", "MacCyrillic", "IBM855", "IBM866",\
                      "ISO-8859-5", "windows-1251", "ISO-8859-2", "windows-1250", "ISO-8859-5",\
                      "windows-1251", "windows-1252", "ISO-8859-7", "windows-1253", "ISO-8859-8",\
                      "windows-1255", "TIS-620"]
    e = []

    for i in encoding_types[::-1]:
        try:
            f = open(fname, "r", encoding=i).read()
            e.append(i)
        except UnicodeDecodeError:
            continue

    print(e)
    return False

if __name__ == '__main__':
    print(get_encoding_type("TestWebsite/Quicksand-Regular.otf"))

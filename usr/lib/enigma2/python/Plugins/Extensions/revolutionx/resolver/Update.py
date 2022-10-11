#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from twisted.web.client import downloadPage
PY3 = sys.version_info.major >= 3
print("Update.py")


def upd_done():        
    print( "In upd_done")
    xfile ='http://patbuweb.com/revolutionlite/revolutionx.tar'
    # print('xfile: ', xfile)
    if PY3:
        xfile = b"http://patbuweb.com/revolutionlite/revolutionx.tar"
        print("Update.py not in PY3")
    fdest = "/tmp/revolutionx.tar"
    # print("upd_done xfile =", xfile)
    downloadPage(xfile, fdest).addCallback(upd_last)


def upd_last(fplug):
    import time
    import os
    time.sleep(5)
    cmd = "tar -xvf /tmp/revolutionx.tar -C /"
    print("cmd A =", cmd)
    os.system(cmd)

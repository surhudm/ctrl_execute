#!/usr/bin/env python

import eups
import os, os.path
from lsst.ctrl.execute.seqFile import SeqFile

def test1():
    filename = os.path.join("/tmp",os.getlogin()+"_"+str(os.getpid())+".seq")
    if os.path.exists(filename) == True:
        os.remove(filename)
    sf = SeqFile(filename)
    a = sf.nextSeq()
    assert a == 0
    a = sf.nextSeq()
    assert a == 1

if __name__ == "__main__":
    test1()

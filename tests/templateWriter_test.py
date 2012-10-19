#!/usr/bin/env python

import eups
import os, os.path, filecmp
from lsst.ctrl.execute.templateWriter import TemplateWriter

def test1():
    pairs = {}
    pairs["TEST1"] = "Hello"
    pairs["TEST2"] = "Goodbye"
    executePkgDir = eups.productDir("ctrl_execute")
    infile = os.path.join(executePkgDir, "tests", "templateWriter.template")
    compare = os.path.join(executePkgDir, "tests", "templateWriter.txt")
    outfile = os.path.join("/tmp",os.getlogin()+"_"+str(os.getpid())+"_template.txt")
    temp = TemplateWriter()
    temp.rewrite(infile, outfile, pairs)
    assert filecmp.cmp(compare,outfile) == True
    

if __name__ == "__main__":
    test1()


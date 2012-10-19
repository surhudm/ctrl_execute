#!/usr/bin/env python

import eups
import os.path
import time
from lsst.ctrl.execute.allocator import Allocator
from lsst.ctrl.execute.allocatorParser import AllocatorParser

def setup():
    test1_args = ["allocatorParser_test",
            "test_platform",
            "-n","64",
            "-s","12",
            "-m","00:30:00",
            "-N","test_set",
            "-q","normal",
            "-e","yes",
            "-O","outlog",
            "-E","errlog",
            "-v",
            ]
    executePkgDir = eups.productDir("ctrl_execute")
    fileName = os.path.join(executePkgDir,"tests","allocator-info1.cfg")
    alp = AllocatorParser(test1_args)
    opts = alp.getOpts()
    al = Allocator("lsst", opts, fileName)
    return al

def test1(al):

    filename1 = al.createUniqueFileName()
    time.sleep(1)
    filename2 = al.createUniqueFileName()
    assert filename1 != filename2

def test2(al):
    executePkgDir = eups.productDir("ctrl_execute")
    fileName = os.path.join(executePkgDir,"tests","config_allocation.cfg")
    nodeSetName1 = al.load(fileName)



if __name__ == "__main__":
    test1(setup())


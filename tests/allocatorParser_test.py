#!/usr/bin/env python

import eups
import os.path
from lsst.ctrl.execute.allocatorParser import AllocatorParser

def test1():
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

    al = AllocatorParser(test1_args)
    opts = al.getOpts()
    args = al.getArgs()

    assert opts.nodeCount == "64"
    assert opts.slots == "12"
    assert opts.maximumWallClock == "00:30:00"
    assert opts.nodeSet == "test_set"
    assert opts.queue == "normal"
    assert opts.email == "yes"
    assert opts.outputLog == "outlog"
    assert opts.errorLog == "errlog"
    assert opts.verbose == True


if __name__ == "__main__":
    test1()

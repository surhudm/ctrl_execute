#!/usr/bin/env python
# 
# LSST Data Management System
# Copyright 2008-2012 LSST Corporation.
# 
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the LSST License Statement and 
# the GNU General Public License along with this program.  If not, 
# see <http://www.lsstcorp.org/LegalNotices/>.
#

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

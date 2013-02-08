#!/usr/bin/env python
# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
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

import sys, os
import argparse
import errno
from lsst.ctrl.execute.dagIdInfoExtractor import DagIdInfoExtractor

def run():
    basename = os.path.basename(sys.argv[0]) 
    
    parser = argparse.ArgumentParser(prog=basename)
    parser.add_argument("-d", "--dagNode", action="store", default=None, dest="dagNode", help="name of dag node to search for", type=str, required=True)
    parser.add_argument("-f", "--filename", action="store", default=None, dest="filename", help="name of dag file to search in", type=str, required=True)

    args = parser.parse_args()

    if os.path.exists(args.filename) == False:
        print "file %s not found" % args.filename
        sys.exit(errno.ENOENT)

    extractor = DagIdInfoExtractor()
    line = extractor.extract(args.dagNode, args.filename)
    if line is not None:
        print line

if __name__ == "__main__":
    run()

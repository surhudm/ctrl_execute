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

# extracts a line from a DAG file to show which ids were processed for a
# particular dag node
def run():
    basename = os.path.basename(sys.argv[0]) 

    dagNode = sys.argv[1]
    filename = sys.argv[2]
    
    if os.path.exists(filename) == False:
        print "file %s not found" % filename
        sys.exit(errno.ENOENT)

    extractor = DagIdInfoExtractor()
    line = extractor.extract(dagNode, filename)
    if line is not None:
        print line

if __name__ == "__main__":
    run()

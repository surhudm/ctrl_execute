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

from __future__ import with_statement
from EnvString import EnvString
import sys, os, os.path

class SeqFile(object):
    def __init__(self, seqFileName):
        self.fileName = EnvString.resolve(seqFileName)

    def nextSeq(self):
        seq = 0
        if os.path.exists(self.fileName) == False:
            self.writeSeq(seq)
        else:
            seq = self.readSeq()
            seq += 1
            self.writeSeq(seq)
        return seq

    def readSeq(self):
        with open(self.fileName) as seqFile:
            line = seqFile.read()
            seq = int(line)
        return seq
        
    def writeSeq(self, seq):
        with open(self.fileName,'w') as seqFile:
            print >>seqFile, seq

if __name__ == "__main__":
    s = SeqFile()
    n = s.nextSeq()
    print n

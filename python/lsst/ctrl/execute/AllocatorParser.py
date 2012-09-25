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
import sys, os, os.path
import optparse, traceback, time

class AllocatorParser(object):
    def __init__(self, argv):

        self.defaults = {}
        
        self.opts = {}
        self.args = []
        
        self.opts, self.args = self.parseArgs(argv)

    def parseArgs(self, argv):
        basename = os.path.basename(argv[0])
        self.usage = """usage: """+basename+""" platform -n node-count -s slots -m minutes [-N node-set]"""
        
        parser = optparse.OptionParser(self.usage)
        parser.add_option("-n", "--node-count", action="store", default=None, dest="nodeCount", help="number of nodes to use")
        parser.add_option("-s", "--slots", action="store", default=None, dest="slots", help="slots per node")
        parser.add_option("-m", "--maximum-wall-clock", action="store", dest="maximumWallClock", default=None, help="maximum wall clock time")
        parser.add_option("-N", "--node-set", action="store", dest="nodeSet", default=None, help="node set name")
        parser.add_option("-q", "--queue", action="store", dest="queue", default=None, help="pbs queue name")
        parser.add_option("-e", "--email", action="store", dest="email", default=None, help="email notification flag")
        parser.add_option("-O", "--output-log", action="store", dest="outputLog", default=None, help="Output log filename")
        parser.add_option("-E", "--error-log", action="store", dest="errorLog", default=None, help="Error log filename")
        parser.add_option("-v", "--verbose", action="store_true", dest="verbose",help="verbose")
        
        opts, args = parser.parse_args(argv)

        if opts.nodeCount is None:
            print "error: required argument --node-count is not specified"
            print self.usage
            sys.exit(10)
        if opts.slots is None:
            print "error: required argument --slots is not specified"
            print self.usage
            sys.exit(10)
        if opts.maximumWallClock is None:
            print "error: required argument --maximum-wall-clock is not specified"
            print self.usage
            sys.exit(10)
        
        if len(args) != 2:
            print "error: required argument 'platform' is not specified"
            print self.usage
            sys.exit(10)


        return opts, args

    def getOpts(self):
        return self.opts

    def getArgs(self):
        return self.args

    def getPlatform(self):
        return self.args[1]


if __name__ == "__main__":
    al = AllocatorParser(sys.argv)
    opts = al.getOpts()
    args = al.getArgs()

    print "opts = ", opts
    print "args = ", args

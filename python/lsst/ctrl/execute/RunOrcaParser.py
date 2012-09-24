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
import re, sys, os, os.path, shutil, subprocess
import optparse, traceback, time
from datetime import datetime
import lsst.pex.config as pexConfig

class RunOrcaParser(object):
    def __init__(self, argv):

        self.defaults = {}
        # TODO: remember to deal with this in the config code
        #self.commandLineDefaults = {}
        #self.commandLineDefaults["USER_NAME"] = os.getlogin()
        #self.commandLineDefaults["USER_HOME"] = os.getenv('HOME')
        
        self.opts = {}
        self.args = []
        
        self.opts, self.args = self.parseArgs(argv)

    def parseArgs(self, argv):
        basename = os.path.basename(argv[0])
        self.usage = """usage: """+basename+""" -e EUPS_PATH -p platform -c command -i id-file [-j ids-per-job] [-d data-directory] [-u user] [-H user-home] [-n node-set] [-r default-root] [-l local-scratch] [-D filesystem-domain]"""
        
        parser = optparse.OptionParser(self.usage)
        parser.add_option("-n", "--node-set", action="store", default=None, dest="nodeSet", help="name of collection of nodes to use")
        parser.add_option("-j", "--ids-per-job", action="store", default=None, dest="idsPerJob", help="ids per job")
        parser.add_option("-r", "--default-root", action="store", dest="defaultRoot", default=None, help="remote working directory for Condor")
        parser.add_option("-l", "--local-scratch", action="store", dest="localScratch", default=None, help="local staging directory for Condor")
        parser.add_option("-d", "--data-directory", action="store", dest="dataDirectory", default=None, help="where the data is located")
        
        
        parser.add_option("-F", "--file-system-domain", action="store", dest="fileSystemDomain", default=None, help="file system domain")
        parser.add_option("-u", "--user-name", action="store", dest="user_name", default=None, help="user")
        parser.add_option("-H", "--user-home", action="store", dest="user_home", default=None, help="home")
        parser.add_option("-i", "--id-file", action="store", dest="inputDataFile", default=None, help="list of ids")
        parser.add_option("-c", "--command", action="store", dest="command", default=None, help="command")
        parser.add_option("-p", "--platform", action="store", dest="platform", default=None, help="platform")
        parser.add_option("-e", "--eups-path", action="store", dest="eupsPath", default=None, help="eups path")
        parser.add_option("-R", "--run-id", action="store", dest="runid", default=None, help="run id")
        parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbose")
        parser.add_option("-s", "--setup", action="append", nargs=2, help="setup")
        
        opts, args = parser.parse_args(argv)

        if opts.eupsPath is None:
            raise RuntimeError("error: required argument --eups-path is not specified")
        if opts.platform is None:
            raise RuntimeError("error: required argument --platform is not specified")
        if opts.command is None:
            raise RuntimeError("error: required argument --command is not specified")
        if opts.inputDataFile is None:
            raise RuntimeError("error: required argument --id-file is not specified")

        return opts, args

    def getOpts(self):
        return self.opts

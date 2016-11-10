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

from __future__ import print_function
from builtins import str
from builtins import object
import os
import pwd
from datetime import datetime
from string import Template
from lsst.ctrl.execute import envString
from lsst.ctrl.execute.allocationConfig import AllocationConfig
from lsst.ctrl.execute.condorConfig import CondorConfig
from lsst.ctrl.execute.condorInfoConfig import CondorInfoConfig
from lsst.ctrl.execute.templateWriter import TemplateWriter
from lsst.ctrl.execute.seqFile import SeqFile


class Plugin(object):

    def runCommand(self, cmd, verbose):
        cmd_split = cmd.split()
        pid = os.fork()
        if not pid:
            # Methods of file transfer and login may
            # produce different output, depending on how
            # the "gsi" utilities are used.  The user can
            # either use grid proxies or ssh, and gsiscp/gsissh
            # does the right thing.  Since the output will be
            # different in either case anything potentially parsing this
            # output (like drpRun), would have to go through extra
            # steps to deal with this output, and which ultimately
            # end up not being useful.  So we optinally close the i/o output
            # of the executing command down.
            #
            # stdin/stdio/stderr is treated specially
            # by python, so we have to close down
            # both the python objects and the
            # underlying c implementations
            if not verbose:
                # close python i/o
                sys.stdin.close()
                sys.stdout.close()
                sys.stderr.close()
                # close C's i/o
                os.close(0)
                os.close(1)
                os.close(2)
            os.execvp(cmd_split[0], cmd_split)
        pid, status = os.wait()
        # high order bits are status, low order bits are signal.
        exitCode = (status & 0xff00) >> 8
        return exitCode

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

class DagIdInfoExtractor(object):
    def extract(self, dagname, filename):
        file = open(filename)
        for line in file:
            line = line.rstrip('\n')

            # look for the line with the dagnode name in it
            if line.find("VARS %s var1=" % dagname) == -1:
                continue
            #
            # At this point, line looks something like this:
            # VARS A1 var1="run=1033 filter=r camcol=2 field=229"

            # split the string into a list
            elements = line.split()

            # recreate the string, without the first two elements
            ids = ' '.join(elements[2:])

            # remove the 'var1=" and the quotes, and return it
            ids = ids[6:].strip('"')
            file.close()
            return ids
        file.close()

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

import math
import argparse
import os
import subprocess
import sys
import time

from textwrap import dedent
import glob
import re


def _line_to_args(self, line):
    for arg in shlex.split(line, comments=True, posix=True):
        if not arg.strip():
            continue
        yield arg


def makeArgumentParser(description, inRootsRequired=True, addRegistryOption=True):

    parser = argparse.ArgumentParser(
        description=description,
        fromfile_prefix_chars="@",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=" \n"
               "ly.")
    parser.convert_arg_line_to_args = _line_to_args


    parser.add_argument(
        "-s", "--source", dest="source",
        help="Source site for file transfer.")

    parser.add_argument(
        "-w", "--workerdir", dest="workerdir",
        help="workers directory")

    parser.add_argument(
        "-t", "--template", dest="template",
        help="template file")

    parser.add_argument(
        "-p", "--prescript", dest="prescript",
        help="pre shell script")

    parser.add_argument(
        "-r", "--runid", dest="runid",
        help="runid of production")

    parser.add_argument(
        "-i", "--idsPerJob", dest="idsPerJob",
        help="number of ids to run per job")

    return parser
 


def writeDagFile(pipeline, templateFile, infile, workerdir, prescriptFile, runid, idsPerJob):
    """
    Write Condor Dag Submission files. 
    """

    print "Writing DAG file "
    print "idsPerJob"
    print idsPerJob

    listSize=idsPerJob

    outname = pipeline + ".diamond.dag"
    mapname = pipeline + ".mapping"

    print outname

    mapObj = open(mapname,"w")
    outObj = open(outname,"w")

    outObj.write("JOB A "+workerdir+"/" + pipeline + ".pre\n"); 
    outObj.write("JOB B "+workerdir+"/" +  pipeline + ".post\n"); 
    outObj.write(" \n"); 

    print "prescriptFile = ",prescriptFile
    if prescriptFile is not None:
        outObj.write("SCRIPT PRE A "+prescriptFile+"\n")

    #
    # A first pass through the Input File to define the individual Jobs
    # Loop over input entries 
    #
    fileObj = open(infile,"r")
    count = 0
    acount = 0
    for aline in fileObj:
        acount+=1
        if acount == listSize:
            count+=1
            outObj.write("JOB A" + str(count) +" "+workerdir+"/" + templateFile + "\n"); 
            acount=0

    outObj.write(" \n"); 

    #
    # A second pass through the Input File constructs variables to
    # be substituted into jobs
    #
    fileObj = open(infile,"r")
    count = 0
    acount = 0
    myDataTotal=""
    myDataList=[]
    newDataTotal=""
    newDataList=[]
    for aline in fileObj:
        acount+=1

 
        myData = aline.rstrip()

        #
        # Construct a string without spaces from the dataids for a job
        # suitable for a unix file name
        #
        # Searching for a space detects 
        # extended input like :  visit=887136081 raft=2,2 sensor=0,1
        # If there is no space, the dataid is something simple like a skytile id  
        if " " in myData:
            # Change space to : 
            myList  = myData.split(' ');
            new1Data = '%s:%s:%s:%s' % tuple(myList)
            # Change = to - 
            myList2  = new1Data.split('=');
            new2Data = '%s-%s-%s-%s-%s' % tuple(myList2)
            # Change , to _ 
            # myList3  = new2Data.split(',');
            # new3Data = '%s_%s_%s_%s' % tuple(myList3)

            # Change filter to f
            myList3  = new2Data.split("filter");
            new3Data = '%sf%s' % tuple(myList3)
            # Change run to r
            myList4  = new3Data.split("run");
            new4Data = '%sr%s' % tuple(myList4)
            # Change camcol to c
            myList5  = new4Data.split("camcol");
            new5Data = '%sc%s' % tuple(myList5)
            # Change field to fd
            myList6  = new5Data.split("field");
            new6Data = '%sfd%s' % tuple(myList6)

            newData=new6Data
            visit = myList[0].split('=')[1]
        else:
            newData=myData
            visit = myData

        myDataList.append(myData)
        newDataList.append(newData)

        # For example:
        # VARS A1 var1="visit=887136081 raft=2,2 sensor=0,1"
        # VARS A1 var2="visit-887136081:raft-2_2:sensor-0_1"

        if acount == listSize:
            count+=1
            myDataTotal  = " X ".join(myDataList)
            newDataTotal = "_".join(newDataList)
            outObj.write("VARS A" + str(count) + " var1=\"" + myDataTotal  + "\" \n")
            # outObj.write("VARS A" + str(count) + " var2=\"" + newDataTotal + "\" \n") 
            outObj.write("VARS A" + str(count) + " var2=\"" + str(count) + "\" \n") 
            outObj.write("VARS A" + str(count) + " visit=\"" + visit + "\" \n") 
            outObj.write("VARS A" + str(count) + " runid=\"" + runid + "\" \n")
            outObj.write("VARS A" + str(count) + " workerid=\"" + str(count) + "\" \n")
            mapObj.write(str(count) + "  " + newDataTotal + "\n")
            mapObj.write(str(count) + "  " + myDataTotal + "\n")
            acount=0
            myDataTotal=""
            newDataTotal=""
            myDataList=[]
            newDataList=[]


    #
    # A third pass through the Input File constructs relationships
    # between the jobs, building a diamond DAG : 1 - N - 1
    #

    fileObj = open(infile,"r")
    count = 0
    acount = 0
    for aline in fileObj:
        acount+=1
        if acount == listSize:
            count+=1
            # PARENT A CHILD A1
            # PARENT A1 CHILD B
            outObj.write("PARENT A CHILD A" + str(count) + " \n"); 
            outObj.write("PARENT A" + str(count) + " CHILD B \n"); 
            acount=0

    outObj.close()
    mapObj.close()


def main():
    print 'Starting generateDag.py'
    parser = makeArgumentParser(description=
        "generateDag.py write a Condor DAG for job submission"
        "by reading input list and writing the attribute as an argument.")
    print 'Created parser'
    ns = parser.parse_args()
    print 'Parsed Arguments'
    print ns
    print ns.idsPerJob

    # SA 
    # templateFile = "SourceAssoc-template.condor"
    # pipeline = "SourceAssoc"
    # infile   = "sky-tiles"

    # Pipeqa  
    # templateFile = "pipeqa-template.template"
    # pipeline = "pipeqa"
    # infile   = "visits-449"

    #   processCcdLsstSim
    pipeline = "S2012Pipe"
    #templateFile = "W2012Pipe-template.condor"
    #infile   = "9429-CCDs.input"

    writeDagFile(pipeline, ns.template, ns.source, ns.workerdir, ns.prescript, ns.runid, int(ns.idsPerJob))


    sys.exit(0)







if __name__ == '__main__':
    main()


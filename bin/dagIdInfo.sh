#!/bin/bash
# Extracts id information for a given dag name
#
# usage: dagIdInfo.sh <dagNode> <dagFileName>
# example: daginfo.sh A100 ~/condor_scratch/test_2013_0207_120130/S2012Pipe.diamond.dag
#
grep -w $1 $2 | grep VARS | grep var1 | awk -v nr=3 '{ for  (x = nr; x <= NF; x++) { printf("%s ", $x);}; print " ";}' | sed 's/var1="//' | sed 's/"  $//'

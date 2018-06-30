#!/usr/bin/python
'''

Takes block of WWIDs and prints a JSON block that can be used in config file for createRACnodes.py like this:

File like this:

600601600ec0360014d62e5fb573e811   UAT_LVMESXIMDB01U_REDO1_614
.
.
.

600601600ec03600d5cce9f6b573e811   UAT_LVMESXIMDB01U_DATA_854


Prints:

"localDisks":[
        {
                "name":       "ASM_DISK1"
                ,"diskType":     "PHYSICAL_DISK"
                ,"size":         0
                ,"shareable":   true
                ,"sparse":       "No"
                ,"description":  "UAT_LVMESXIMDB01U_REDO1_614"
                ,"obj":          null
                ,"wwid":         "600601600ec0360014d62e5fb573e811"
        }
		.
		.
		.

        ,{
                "name":       "ASM_DISK13"
                ,"diskType":     "PHYSICAL_DISK"
                ,"size":         0
                ,"shareable":   true
                ,"sparse":       "No"
                ,"description":  "UAT_LVMESXIMDB01U_DATA_854"
                ,"obj":          null
                ,"wwid":         "600601600ec03600d5cce9f6b573e811"
        }
]
You may want to update ALLDISKS in params.ini to this:
ALLDISKS=/dev/xvdc . . . . /dev/xvdo
"

'''

import json
import os
import argparse

parser = argparse.ArgumentParser(description="Creates the json block for all WWIDs in config file passed as arg")
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-configFile", "-c",      help="file containing block of wwids", required=True)
args = parser.parse_args()


wwids = []
with open(args.configFile) as f:
    wwids = f.read().splitlines()

asmDiskNo=0

print "\"localDisks\":[ "

for line in wwids:
	if len(line) < 1:
		continue
	details=line.split(',')
	wwid=details[0]
	description=details[1]
	'''
		{ "name":	     "ASM_DISK1"
		,"diskType":     "PHYSICAL_DISK"
        ,"size":         5
        ,"shareable":   true
        ,"sparse":       "No"
        ,"description":  "ASM RAC Shared Disk TonyA testing"
        ,"obj":          null
        ,"wwid":         "600601600ec03600cb545b949352e811"
        },
	'''
	asmDiskNo += 1
	if asmDiskNo == 1:
		print "\t{"	
	else:
		print "\t,{"	
	print "\t\t\"name\":	      \"ASM_DISK{}\"    ".format(asmDiskNo)
	print "\t\t,\"diskType\":     \"PHYSICAL_DISK\" "
	print "\t\t,\"size\":         0         "
	print "\t\t,\"shareable\":   true               "
	print "\t\t,\"sparse\":       \"No\"            "
	print "\t\t,\"description\":  \"{}\"            ".format(description)
	print "\t\t,\"obj\":          null              "
	print "\t\t,\"wwid\":         \"{}\"            ".format(wwid)
	print "\t}                                "

print "]"


print "You may want to update ALLDISKS in params.ini to this: "

ALLDISKS="ALLDISKS="
# print from /dev/xvdc ... 
for dn in [ chr(i + 98) for i in range(1,asmDiskNo + 1) ]:
	ALLDISKS += "/dev/xvd" + dn + " "
	
print ALLDISKS



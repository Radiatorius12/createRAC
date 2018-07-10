#!/usr/bin/python
'''

Updates localDisks tuple of the createRACnodes.py config file 

Example:

[automate@lvmjenkinsu createRAC]$ cat defaultLocalDisks
DBSCRIPTS_DISK,5,Yes,local disk for /dbscripts,null
ORACHK_DISK,5,Yes,local disk for /orachk,null
OPROEM001_DISK,5,Yes,local disk for /oproem001,null
OSWATCHER_DISK,5,Yes,local disk for /oswatcher,null

Example Usage:
[automate@lvmjenkinsu createRAC]$ ./createLocalDisksJsonConf.py -f defaultLocalDisks  -c createRacDEMO.json

createRacDEMO.json will be updated if user types "yes" to confirm and a backup file is created, e.g. createRacDEMO.json.20180703_155747

'''


import json
import os
import argparse
import createRACnodes

parser = argparse.ArgumentParser(description="Creates the json block local disks to be created on each node")
parser.add_argument("-verbose", "-v",    action="store_true")
parser.add_argument("-localDisks", "-f",   help="file containing local disks to be created on each node ", required=True)
parser.add_argument("-configFile", "-c", help="configuration of the build in json format")
args = parser.parse_args()

lines = []
with open(args.localDisks) as f:
    lines = f.read().splitlines()

localDisksJson=[]
fields=[ "name", "size", "sparse", "description", "repository"]
for line in lines:
	if len(line) < 1:
		continue		
	disk = { "diskType":	"VIRTUAL_DISK", "shareable":   False}
	# name,size_GB,spares_Yes_or_No,description
	i = 0
	for f in line.split(','):
		#print fields[i], f
		disk[ fields[i] ] = f
		i += 1
	localDisksJson.append( disk )

if args.verbose:
	print json.dumps(localDisksJson,indent=2)

if args.configFile:
	confirm = raw_input("update localDisks for all nodes in {} \"yes\" to confirm:".format(args.configFile)).lower()
else:
	exit(0)

if confirm != "yes":
	print json.dumps(localDisksJson,indent=2)
	exit(0)

conf = createRACnodes.StateFile(args.configFile)

try:
	with open(conf.getName(), "r") as f:
		myConfig = json.load(f)
except ValueError as error:
	print("Config file {} is not valid JSON".format(conf.getName()))
	exit(1)
except Exception as error:
	print("Failed to load RAC Config from file {} error-> {}".format(conf.getName(), error))
	exit(1)


for racnode in myConfig["racnodes"]:
	racnode["localDisks"]=localDisksJson
conf.save(myConfig)

asmDisks = myConfig["asmDisks"]
if asmDisks is not None:
	print "Warning:  asmDisks is already set.   Consider running createAsmDisksConf.py once more and check the ALL_DISKS suggestion"






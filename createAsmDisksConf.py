#!/usr/bin/python
'''

Updates asmDisks tuple of the createRACnodes.py config file 

Example:

[automate@lvmjenkinsu createRAC]$ cat RacDEMO_phys_disks
600601600ec03600cb545b949352e811,ASM_DISK1
600601600ec036005bbdbdb89352e811,ASM_DISK2
600601600ec03600439f993e9452e811,ASM_DISK3
600601600ec036004d8edbd89352e811,ASM_DISK4
600601600ec036008ae4b6179452e811,ASM_DISK5

Example Usage:


[automate@lvmjenkinsu createRAC]$ ./createAsmDisksConf.py -f RacDEMO_phys_disks -c createRacDEMO.json
You may want to update ALLDISKS in params.ini to this:
ALLDISKS=/dev/xvdc /dev/xvdd /dev/xvde /dev/xvdf /dev/xvdg


'''

import json
import os
import argparse
import createRACnodes


parser = argparse.ArgumentParser(description="Creates the json block for all WWIDs in config file passed as arg")
parser.add_argument("-verbose", "-v",    action="store_true")
parser.add_argument("-asmDisks", "-f",   help="file containing wwids, optional disk name to be mapped as asm disks ", required=True)
parser.add_argument("-configFile", "-c", help="configuration of the build in json format")
args = parser.parse_args()


lines = []
with open(args.asmDisks) as f:
    lines = f.read().splitlines()

asmDiskNo=0
asmDisksJson=[]
fields=[ "wwid", "description" ]
for line in lines:
	if len(line) < 1:
		continue
	asmDiskNo += 1

	disk = { "diskType": "PHYSICAL_DISK", "shareable":  True, "sparse": "No"}
	disk[ "name" ] = "ASM_DISK{}".format(asmDiskNo)
	i = 0
	for f in line.split(','):
		#print fields[i], f
		disk[ fields[i] ] = f
		i += 1
	asmDisksJson.append( disk )

if args.verbose:
	print json.dumps(asmDisksJson,indent=2)

print "You may want to update ALLDISKS in params.ini to this: "

ALLDISKS="ALLDISKS="
# print from /dev/xvdc ... 
for dn in [ chr(i + 98) for i in range(1,asmDiskNo + 1) ]:
	ALLDISKS += "/dev/xvd" + dn + " "
	
print ALLDISKS

if args.configFile:
	confirm = raw_input("update asmDisks for all nodes in {} \"yes\" to confirm:".format(args.configFile)).lower()
else:
	exit(0)

if confirm != "yes":
	print json.dumps(asmDisksJson,indent=2)
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

conf.save(myConfig)

myConfig["asmDisks"]=asmDisksJson

conf.save(myConfig)




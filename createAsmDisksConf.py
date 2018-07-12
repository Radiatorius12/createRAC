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

noOfAsmDisks=0
asmDisksJson=[]
fields=[ "wwid", "description" ]
for line in lines:
	if len(line) < 1:
		continue
	noOfAsmDisks += 1

	disk = { "diskType": "PHYSICAL_DISK", "shareable":  True, "sparse": "No"}
	disk[ "name" ] = "ASM_DISK{}".format(noOfAsmDisks)
	i = 0
	for f in line.split(','):
		#print fields[i], f
		disk[ fields[i] ] = f
		i += 1
	asmDisksJson.append( disk )

if args.verbose:
	print json.dumps(asmDisksJson,indent=2)

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

myConfig["asmDisks"]=asmDisksJson

conf.save(myConfig)

# look for global local disk setting
localDisks = myConfig.get("localDisks")
noOfLocalDisks = 0
if localDisks is None:
	# get setting from 1st node
	node1 = myConfig["racnodes"][0]
	localDisks = node1.get("localDisks")
	if localDisks is not None:
		print "Re-calculating ALLDISKS setting - offsetting due to discovery of localDisks"
		noOfLocalDisks = len(localDisks)
		print "noOfLocalDisks ", noOfLocalDisks

print "You may want to update ALLDISKS in params.ini to this: "

#  ALLDISKS="ALLDISKS="
#  # print from /dev/xvdc ... 
#  for dn in [ chr(i + 98 + noOfLocalDisks) for i in range(1,noOfAsmDisks + 1) ]:
#  	ALLDISKS += "/dev/xvd" + dn + " "
#  
#  print ALLDISKS




ALLDISKS="ALLDISKS="
'''
	(1) /dev/xvda - template system disk
	(2) /dev/xvdb - template system disk
	(3) -> (3 + noOfLocalDisks) /dev/xvdc -> /dev/xvd? - local disks 
	(3 + noOfLocalDisks) -> (?) /dev/xvd? -> /dev/xvd? - asm disks
'''
diskCount=0
for i in range( 2 + noOfLocalDisks, 2 + noOfLocalDisks + noOfAsmDisks):
	# print 'a' => 0    ord('a') => 97
	# print 'z' => 25   ord('z') => 122
	diskCount += 1
	dn=""
	chrA = ""
	a = i // 26
	b = i % 26
	#print "i={} a={} b={}".format(i,a,b)
	if a > 0:
		chrA="{}".format( chr(a + 96) )
	dn="{}{}".format(  chrA, chr(b + 97) )
	#print "{}      \"{}\"	".format(diskCount,dn)
	ALLDISKS += "/dev/xvd" + dn + " "

print ALLDISKS




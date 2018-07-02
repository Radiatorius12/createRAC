#!/bin/python

'''

./createDiskMapping.py -ovmConfig <json file with OVM connection config> -wwid  <WWID of disk to me mapped> -vmId <OVM Object ID of Disk>
Example:

cd /home/automate/ovm/createRAC

cat eximBillsUAT_OVM.json
{
    "ovmHost":           "10.119.9.60"
    ,"port":              7002
    ,"baseUri":           "/ovm/core/wsapi/rest"
    ,"ovm_user":          "admin"
}

./createDiskMapping.py -c UAT_OVM.json -wwid 600601600E3600CC2153EFA67AE811 -vmId 0004fb0000060000cfc71a951de69201
./createDiskMapping.py -c UAT_OVM.json -wwid 600601600ec03600cb545b949352e811 -vmId 0004fb00000600004ea7d13045e4d77e

./createDiskMapping.py -c UAT_OVM.json -wwid 600601600ec036005bbdbdb89352e811 -vmName racphys0



Status:
	NEED TO TEST

'''

import requests
import json
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import getpass
try:
	import passwdPkg
except Exception as e:
	print "Warning: could not load passwdPkg : {}".format(e)
import createRACnodes

parser = argparse.ArgumentParser(description="Create Mapping between VM and Physical Disk (wwid)")
parser.add_argument("-ovmConfig","-c"  ,help="OVM json config file", required=True)
parser.add_argument("-debug"           ,help="set debugging", action="store_true")

disk_group =  parser.add_mutually_exclusive_group(required=True)
disk_group.add_argument("-wwid", "-w"          ,help="WWID of Physical Disk (get from SAN team)")
disk_group.add_argument("-listofWWIDs", "-l"   ,help="file containing list WWIDs of Physical Disks (get from SAN team)")

vm_group =  parser.add_mutually_exclusive_group(required=True)
vm_group.add_argument("-vmId","-id"             ,help="OVM ID of Vm (get from OVM)")
vm_group.add_argument("-vmName","-name","-n"    ,help="OVM name of Vm (get from OVM)")

args = parser.parse_args()

'''
	Load configuration of OVM
'''

debug = createRACnodes.Debug(args.debug)
#createRACnodes.debug=args.debug

try:
	with open(args.ovmConfig, "r") as f:
		myConfig = json.load(f)
except ValueError as e:
	print "The ovmConfig file \"{}\" is not valid json".format(args.ovmConfig)
	exit(1)

'''
	Connect to OVM
'''
if myConfig.get("ovm_pw") is None:
	ovm_vault_name = myConfig.get("ovm_vault_name")
	if ovm_vault_name is not None:
		try:
			myConfig["ovm_pw"]=passwdPkg.getOVMPasswd(ovm_vault_name,'admin')
		except Exception as e:
			print e
		if myConfig.get("ovm_pw") is None:
			myConfig["ovm_pw"] = getpass.getpass("OVM admin password: ")

s=requests.Session()
s.auth=( myConfig["ovm_user"], myConfig["ovm_pw"] )
s.verify=False #disables SSL certificate verification
s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
baseUri="https://{host}:{port}{uri}".format(host=myConfig["ovmHost"],
											 port=myConfig["port"],
											 uri=myConfig['baseUri'])


'''
	Get StorageElement object for the Disk with WWID
'''

diskToBeMapped = []
if args.listofWWIDs:
	wwids = []
	with open(args.listofWWIDs) as f:
		wwids = f.read().splitlines()
	diskNo = 0
	for line in wwids:
		if len(line) < 1:
			continue
		diskNo += 1
		details=line.split(',')
		wwid=details[0]
		description=""
		if len(details) > 1:
			description=details[1]
		diskToBeMapped.append({
							"name":          "ASM_DISK{}".format({diskNo})
							,"diskType":     "PHYSICAL_DISK"
							,"size":         0
							,"shareable":    True
							,"sparse":       "No"
							,"description":  "{}".format({description})
							,"obj":          None
							,"wwid":         wwid
					})
else:
	diskToBeMapped = [ {
								"name":          "ASM_DISK1"
								,"diskType":     "PHYSICAL_DISK"
								,"size":         0
								,"shareable":    True
								,"sparse":       "No"
								,"description":  ""
								,"obj":          None
								,"wwid":         args.wwid
						} ]


debug.prt ( "Disk Object:"                                                   )
debug.prt ( "==============================================================" )
debug.prt ( ( json.dumps(diskToBeMapped, indent=2) )                                )
debug.prt ( "==============================================================" )

'''
	Get vm object 
'''
racNodeObj = ""
if args.vmId is not None:
	racNodeObj=createRACnodes.get_obj_from_id(s,baseUri,"Vm",args.vmId)
else:
	racNodeObj=createRACnodes.get_obj_from_name(s,baseUri,"Vm",args.vmName)
	
debug.prt ( "Vm Object:"                                                     )
debug.prt ( "==============================================================" )
debug.prt ( ( json.dumps(racNodeObj, indent=2) )                             )
debug.prt ( "==============================================================" )

createRACnodes.createVmDiskMapping(s,baseUri,racNodeObj,diskToBeMapped)




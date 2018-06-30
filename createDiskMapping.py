#!/bin/python

'''

./createDiskMapping.py -ovmConfig <json file with OVM connection config> -wwid  <WWID of disk to me mapped> -vmId <OVM Object ID of Disk>
Example:

cd /home/automate/ovm/createRAC

cat myBillsUAT_OVM.json
{
    "ovmHost":           "x.y.z.60"
    ,"port":              7002
    ,"baseUri":           "/ovm/core/wsapi/rest"
    ,"ovm_user":          "admin"
    ,"ovm_pw":            "<password>"
    ,"templateName":      "OVM_OL7U5_X86_64_12102DBRAC_PVHVM-1of2.tar.gz"
    ,"templateNameId":    null
    ,"repository":	      "UAT_POC_Repo"
    ,"repositoryId":      null
    ,"repositoryIdObj":   null
    ,"serverPool":	      "UAT_POC"
    ,"serverPoolId":      null
}

./createDiskMapping.py -ovmConfig myBillsUAT_OVM.json -wwid 600601600ec03600d5cce9f6b573e811 -vmId 0004fb0000060000cfc71a951de69201


Status:
	NEED TO TEST

'''

import requests
import json
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import createRACnodes

parser = argparse.ArgumentParser(description="Create Mapping between VM and Physical Disk (wwid)")
parser.add_argument("-ovmConfig"       ,help="OVM json config file", required=True)
parser.add_argument("-vmId"            ,help="OVM ID of Vm (get from OVM)", required=True)
parser.add_argument("-wwid"            ,help="WWID of Physical Disk (get from SAN team)", required=True)
parser.add_argument("-debug"           ,help="set debugging", action="store_true")

args = parser.parse_args()

'''
	Load configuration of OVM
'''

debug = createRACnodes.Debug(args.debug)
#createRACnodes.debug=args.debug

try:
	with open(args.ovmConfig, "r") as f:
		myConfig = json.load(f)

except Exception as error:
	print("Failed to load RAC Config from file {} error-> {}".format(conf.getName(), error))
	exit()

'''
	Connect to OVM
'''

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

# Its array due to implementation in createRACnodes - but here we can only map one disk at the moment.
diskToBeMapped = [ {
							"name":          "ASM_DISK1"
							,"diskType":     "PHYSICAL_DISK"
							,"size":         0
							,"shareable":    True
							,"sparse":       "No"
							,"description":  ""
							,"obj":          None
							,"wwid":         ""
					} ]

#diskToBeMapped[0]["obj"] = createRACnodes.getDiskObjByWwid(s,baseUri,args.wwid)
diskToBeMapped[0]["wwid"] = args.wwid

debug.prt ( "Disk Object:"                                                   )
debug.prt ( "==============================================================" )
debug.prt ( ( json.dumps(diskToBeMapped, indent=2) )                                )
debug.prt ( "==============================================================" )

'''
	Get vm object 
'''
racNodeObj=createRACnodes.get_obj_from_id(s,baseUri,"Vm",args.vmId)

debug.prt ( "Vm Object:"                                                     )
debug.prt ( "==============================================================" )
debug.prt ( ( json.dumps(racNodeObj, indent=2) )                             )
debug.prt ( "==============================================================" )


createRACnodes.createVmDiskMapping(s,baseUri,racNodeObj,diskToBeMapped)




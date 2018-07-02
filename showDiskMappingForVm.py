#!/usr/bin/python
'''

[automate@lvmjenkinsu createRAC]$ ./showDiskMappingForVm.py -c UAT_OVM.json -n racphys0
------------------------------------------------------------------------------------------------------------------------------------
Virtual Disk: 0 "System.img (16)" size 15.0 GB shareable=False description=""
Virtual Disk: 1 "Oracle12102DBRAC_x86_64-xvdb.img (22)" size 45.0 GB shareable=False description=""
------------------------------------------------------------------------------------------------------------------------------------
Physical Disk: 2 WWID : 600601600ec03600cb545b949352e811 OVM Disk: "DGC (19)" size 5.0 GB shareable=True description="RAC Testing TonyA"
Physical Disk: 6 WWID : 600601600ec036008ae4b6179452e811 OVM Disk: "DGC (14)" size 50.0 GB shareable=True description="RAC Testing TonyA"
Physical Disk: 5 WWID : 600601600ec036004d8edbd89352e811 OVM Disk: "DGC (37)" size 5.0 GB shareable=True description="RAC Testing TonyA"
Physical Disk: 4 WWID : 600601600ec03600439f993e9452e811 OVM Disk: "DGC (10)" size 50.0 GB shareable=True description="RAC Testing TonyA"
Physical Disk: 3 WWID : 600601600ec036005bbdbdb89352e811 OVM Disk: "DGC (38)" size 5.0 GB shareable=True description="RAC Testing TonyA"
------------------------------------------------------------------------------------------------------------------------------------
[automate@lvmjenkinsu createRAC]$ ./showDiskMappingForVm.py -c UAT_OVM.json -n racphys0 -delete
------------------------------------------------------------------------------------------------------------------------------------
Virtual Disk: 0 "System.img (16)" size 15.0 GB shareable=False description=""
Virtual Disk: 1 "Oracle12102DBRAC_x86_64-xvdb.img (22)" size 45.0 GB shareable=False description=""
------------------------------------------------------------------------------------------------------------------------------------
Physical Disk: 2 WWID : 600601600ec03600cb545b949352e811 OVM Disk: "DGC (19)" size 5.0 GB shareable=True description="RAC Testing TonyA"
Do you want to delete this disk mapping?  Options ["y"|"all"] : all
Deleting mapping from vm 0004fb00000600004ea7d13045e4d77e to 0004fb00001300001a5463d23eed994d...
Delete VM Disk Mapping: Mapping for disk Id (0004fb000018000087b7c399f3c4f7ef) from VM: racphys0: SUCCESS

Done
Physical Disk: 6 WWID : 600601600ec036008ae4b6179452e811 OVM Disk: "DGC (14)" size 50.0 GB shareable=True description="RAC Testing TonyA"
Deleting mapping from vm 0004fb00000600004ea7d13045e4d77e to 0004fb00001300008ca8af3fbdbcac68...
Delete VM Disk Mapping: Mapping for disk Id (0004fb00001800007864ef5ac86c3845) from VM: racphys0: SUCCESS

Done
Physical Disk: 5 WWID : 600601600ec036004d8edbd89352e811 OVM Disk: "DGC (37)" size 5.0 GB shareable=True description="RAC Testing TonyA"
Deleting mapping from vm 0004fb00000600004ea7d13045e4d77e to 0004fb0000130000874d3339e0865fb6...
Delete VM Disk Mapping: Mapping for disk Id (0004fb00001800005bd9169a5ab74eca) from VM: racphys0: SUCCESS

Done
Physical Disk: 4 WWID : 600601600ec03600439f993e9452e811 OVM Disk: "DGC (10)" size 50.0 GB shareable=True description="RAC Testing TonyA"
Deleting mapping from vm 0004fb00000600004ea7d13045e4d77e to 0004fb0000130000de4136fdb1b60ff7...
Delete VM Disk Mapping: Mapping for disk Id (0004fb000018000011d598e1541307c7) from VM: racphys0: SUCCESS

Done
Physical Disk: 3 WWID : 600601600ec036005bbdbdb89352e811 OVM Disk: "DGC (38)" size 5.0 GB shareable=True description="RAC Testing TonyA"
Deleting mapping from vm 0004fb00000600004ea7d13045e4d77e to 0004fb00001300000d3f196be832bae6...
Delete VM Disk Mapping: Mapping for disk Id (0004fb0000180000e95b13100029ed44) from VM: racphys0: SUCCESS

Done
------------------------------------------------------------------------------------------------------------------------------------

cat C:\tony\Automation\Phoenix\RAC\OVM\createRAC\racphys_wwids
600601600ec03600cb545b949352e811
600601600ec036005bbdbdb89352e811
600601600ec03600439f993e9452e811
600601600ec036004d8edbd89352e811
600601600ec036008ae4b6179452e811


DISKS MUST BE IN Required Target order


[automate@lvmjenkinsu createRAC]$ ./createDiskMapping.py  -c UAT_OVM.json -n racphys0 -l racphys_wwids
==============================================================
createVmDiskMapping called to map disks for racphys0
==============================================================
Create VM Disk Mapping: Mapping for disk Id (0004fb000018000087b7c399f3c4f7ef) on VM: racphys0: SUCCESS

Create VM Disk Mapping: Mapping for disk Id (0004fb000018000087b7c399f3c4f7ef) on VM: racphys0 Mapping Created
Create VM Disk Mapping: Mapping for disk Id (0004fb0000180000e95b13100029ed44) on VM: racphys0: SUCCESS

Create VM Disk Mapping: Mapping for disk Id (0004fb0000180000e95b13100029ed44) on VM: racphys0 Mapping Created
Create VM Disk Mapping: Mapping for disk Id (0004fb000018000011d598e1541307c7) on VM: racphys0: SUCCESS

Create VM Disk Mapping: Mapping for disk Id (0004fb000018000011d598e1541307c7) on VM: racphys0 Mapping Created
Create VM Disk Mapping: Mapping for disk Id (0004fb00001800005bd9169a5ab74eca) on VM: racphys0: SUCCESS

Create VM Disk Mapping: Mapping for disk Id (0004fb00001800005bd9169a5ab74eca) on VM: racphys0 Mapping Created
Create VM Disk Mapping: Mapping for disk Id (0004fb00001800007864ef5ac86c3845) on VM: racphys0: SUCCESS

Create VM Disk Mapping: Mapping for disk Id (0004fb00001800007864ef5ac86c3845) on VM: racphys0 Mapping Created



[automate@lvmjenkinsu createRAC]$ ./showDiskMappingForVm.py -c UAT_OVM.json -n racphys0
------------------------------------------------------------------------------------------------------------------------------------
Virtual Disk: 0 "System.img (16)" size 15.0 GB shareable=False description=""
Virtual Disk: 1 "Oracle12102DBRAC_x86_64-xvdb.img (22)" size 45.0 GB shareable=False description=""
------------------------------------------------------------------------------------------------------------------------------------
Physical Disk: 4 WWID : 600601600ec03600439f993e9452e811 OVM Disk: "DGC (10)" size 50.0 GB shareable=True description="RAC Testing TonyA"
Physical Disk: 5 WWID : 600601600ec036004d8edbd89352e811 OVM Disk: "DGC (37)" size 5.0 GB shareable=True description="RAC Testing TonyA"
Physical Disk: 2 WWID : 600601600ec03600cb545b949352e811 OVM Disk: "DGC (19)" size 5.0 GB shareable=True description="RAC Testing TonyA"
Physical Disk: 3 WWID : 600601600ec036005bbdbdb89352e811 OVM Disk: "DGC (38)" size 5.0 GB shareable=True description="RAC Testing TonyA"
Physical Disk: 6 WWID : 600601600ec036008ae4b6179452e811 OVM Disk: "DGC (14)" size 50.0 GB shareable=True description="RAC Testing TonyA"
------------------------------------------------------------------------------------------------------------------------------------


'''
import requests
import json
import time
import getpass
try:
	import passwdPkg
except Exception as e:
	print "Warning: could not load passwdPkg : {}".format(e)
import createRACnodes
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


def getDiskTargetCount(s,baseUri,vmId):
	vmObj=createRACnodes.get_obj_from_id(s,baseUri,"Vm",vmId)
	vmDiskMappingIds = vmObj['vmDiskMappingIds']
	diskTargetCount = len(vmDiskMappingIds)
	return diskTargetCount


def getDiskmappingsForVm(s,baseUri,vmId):

	diskCount=getDiskTargetCount(s,baseUri,vmId)
	print "DISK COUNT " ,diskCount
	print "----------------"

	mappings = [ None ] * diskCount
	r=s.get(baseUri+'/VmDiskMapping').json()
	for mapping in r:
		if mapping["vmId"]["value"] == vmId:
			diskTarget=mapping["diskTarget"]
			mappings[diskTarget]=mapping
			#mappings.append(mapping)
	return mappings

def getPhysicalDisk(s,baseUri,id):
	r=s.get(baseUri+'/StorageElement').json()
	for disk in r:
		if disk["id"]["value"] == id:
			return disk

def getVirtalDisk(s,baseUri,id):
	r=s.get(baseUri+'/VirtualDisk').json()
	for disk in r:
		if disk["id"]["value"] == id:
			return disk

def deleteDiskMapping(s,baseUri,vmId,mappedObjId):
	print "Deleting mapping from vm {vmId} to {mappedObjId}...".format(vmId=vmId,mappedObjId=mappedObjId )
	uri='{base}/Vm/{vmId}/VmDiskMapping/{mappedObjId}'.format(
												base=baseUri,
												vmId=vmId,
												mappedObjId=mappedObjId)
	job=s.delete(uri).json()
	if "errorCode" not in job:
		jobResult=createRACnodes.wait_for_job(s,job['id']['uri'])
		if jobResult['jobSummaryState'] == 'SUCCESS':
			print
			print "Done"
		else:
			print ( "JOB Failed:"                                                    )
			print ( "==============================================================" )
			print ( json.dumps(jobResult, indent=2)                                  )
			print ( "==============================================================" )
			raise Exception('see above error')
	else:
		raise Exception('Submit Job failed: {error}'.format( error=json.dumps( job, indent=2 )))

# end of deleteDiskMapping() ------------------------------

'''
 ======================================================================

	Start Here

 ======================================================================
'''
parser = argparse.ArgumentParser(description="Shows Disk mapping for a Vm")
parser.add_argument("-ovmConfig","-c"  ,help="OVM json config file", required=True)
parser.add_argument("--verbose", "-v", action="store_true")

vm_group =  parser.add_mutually_exclusive_group(required=True)
vm_group.add_argument("-vmId","-id"             ,help="OVM ID of Vm (get from OVM)")
vm_group.add_argument("-vmName","-name","-n"    ,help="OVM name of Vm (get from OVM)")


parser.add_argument("-deleteMapping", help="delete Physical Disk mapping", action="store_true")
args = parser.parse_args()

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


if args.vmName is not None:
	try:
		vmId=createRACnodes.get_id_from_name(s,baseUri,'Vm',args.vmName)
	except:
		pass
	if vmId is None:
		print "Cant find {vm}, check name and try again".format(vm=args.vmName)
		exit(1)
else:
	vmId=args.vmId



print "------------------------------------------------------------------------------------------------------------------------------------"

diskMappings=getDiskmappingsForVm(s,baseUri,vmId)
for mapping in diskMappings:
	if mapping.get("virtualDiskId"):
		if args.verbose:
			print "Virtual Disk: " + json.dumps(mapping["virtualDiskId"], indent=2, sort_keys=True)
		virtDisk=getVirtalDisk(s,baseUri,mapping["virtualDiskId"]["value"])
		print "Virtual Disk: {diskTarget} \"{ovm}\" size {size:.1f} GB shareable={shareable} description=\"{desc}\"".format(
			diskTarget=mapping["diskTarget"],
			ovm=virtDisk["name"],
			size=virtDisk["size"] / 1024 / 1024 / 1024,
			shareable=virtDisk["shareable"],
			desc=virtDisk["description"]
			)

print "------------------------------------------------------------------------------------------------------------------------------------"
deleteAll = False
for mapping in diskMappings:
	if mapping.get("storageElementId"):
		if args.verbose:
			print "Physical Disk:" + json.dumps(mapping["storageElementId"], indent=2, sort_keys=True)
		phyDisk=getPhysicalDisk(s,baseUri,mapping["storageElementId"]["value"])
		print "Physical Disk: {diskTarget} WWID : {wwid} OVM Disk: \"{ovm}\" size {size:.1f} GB shareable={shareable} description=\"{desc}\"".format(
					diskTarget=mapping["diskTarget"],
					wwid=phyDisk["page83Id"][-32:],
					ovm=phyDisk["name"],
					size=phyDisk["size"] / 1024 / 1024 / 1024,
					shareable=phyDisk["shareable"],
					desc=phyDisk["description"]
					)
		#print "Mapping ID : ",mapping["id"]["value"]
		deleteThis = False
		if args.deleteMapping and not deleteAll:
			confirm = raw_input("Do you want to delete this disk mapping?  Options [\"y\"|\"all\"] : ").lower()
			if confirm == "all":
				deleteAll = True
			elif confirm == "y":
				deleteThis = True
			else:
				print ""
				continue

		if deleteAll or deleteThis:
			#print "deleteDiskMapping {} {}".format(vmId,mapping["id"]["value"])
			deleteDiskMapping(s,baseUri,vmId,mapping["id"]["value"])

print "------------------------------------------------------------------------------------------------------------------------------------"



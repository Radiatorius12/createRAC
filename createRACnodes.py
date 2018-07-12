#!/bin/python

'''
	The following TODO list depends on the Terraform plug in progress which would replace this script however, procs
	here could be re-used in the plugin but would need to be converted to golang.

	To Do
		MUST:
			-o- IMPORTANT- make sure / update Physical disks => sharable
				===>>> Started this but commented out as setSharable function fails... need to fix
			-o- (for use with oracle's deploycluster.py script)
				include updating / preparing a params.ini


		SHOULD:
			-o- private IPs AND ? OR change NIC setting in template so that the private NIC is local host only
			-o- VLAN :  currently using the VLAN setting in the template
			-o- Default GW - currently hardcode in rac config file.   Needs to be aligned with the VLAN setting

			NICE TO HAVE:
			-o- For apply option, check to see if objs exists
			-o- Change template disk names
			-o- Add "plan" option - like terraform
			For plan and discovery functionallity:
				-o- For Disks
					+ virtual_disks - add mapping id
					+ phy disks - add storage element id
								- add mapping array
			For apply and plan:
				-o- For Nodes
					+ check to see if the object exists
						use obj in json state file
						chk to see if name exists
				-o- For Disks
					+ check to see if the object exists
						use obj in json state file
				-o- For Disk Mapping
					- 

	Option to have explicit REPO ID for the Virtual disks added.  In the json file it would like this:

	{ "name":	     "ASM_DISK1"
			,"diskType":	"VIRTUAL_DISK"
			,"repositoryId": "0004fb00000500009d1a4d06869a2eaf"
			,"size":        5
			,"shareable":   true
			,"sparse":      "No"
			,"description": "ASM RAC Shared Disk TonyA testing"
			,"obj":         null
	}

	Working version from 6th Jul 2018
'''

import requests
import json
import time
import os
import argparse
from shutil import copyfile
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import datetime

import getpass
try:
	import passwdPkg
except Exception as e:
	print "Warning: could not load passwdPkg : {}".format(e)

try:
	import ipAddressPkg
except:
	pass

class Debug:
	debugFlag = False

	def __init__(self, b):
		self.debugFlag = b

	def setDebug(self, b):
		self.debugFlag = b

	def getDebug(self):
		return self.debugFlag

	def prt(self, txt):
		if self.debugFlag:
			now=datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")
			print "{} {}".format(now, txt)

class StateFile:
	oldStateFiles = []
	stateFileName = ""

	# The init method or constructor
	def __init__(self, n):
		self.stateFileName = n

	def purgeOld(self):
		for f in self.oldStateFiles:
			try:
				#print "rm {}".format(f)
				os.remove(f)
			except OSError as e:
				#print "Warning: failed to delete {} : {}".format(f,str(e))
				pass

	def printStateFile(self):
		print self.stateFileName

	def getName(self):
		return self.stateFileName

	def save(self,d):
		stateFileName = self.stateFileName
		if os.path.isfile(stateFileName):
			now=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
			stateFileOld="{}.{}".format(stateFileName, now)
			copyfile(stateFileName, stateFileOld)
			self.oldStateFiles.append(stateFileOld)
		with open(stateFileName,'w') as f:
			json.dump(d, f, indent=2)

	def showStateFiles(self):
		n = 1
		for f in self.oldStateFiles:
			print "{}: {}".format(n,f)
			n += 1

def get_idObj_from_name(s,baseUri,obj,name):
	#Usage: templateId=get_id_from_name(s,baseUri,'Vm','OVM_OL7U5_X86_64_12102DBRAC_PVHVM-1of2.tar.gz')
	r=s.get(baseUri+'/'+obj)
	for i in r.json():
		if i['name'] == name:
			idObj = i['id']
			return idObj
	return None

def get_id_from_name(s,baseUri,obj,name):
	#Usage: templateId=get_id_from_name(s,baseUri,'Vm','OVM_OL7U5_X86_64_12102DBRAC_PVHVM-1of2.tar.gz')
	r=s.get(baseUri+'/'+obj)
	for i in r.json():
		if i['name'] == name:
			id = i['id']['value']
			return id
	return None

def get_obj_from_name(s,baseUri,obj,name):
	uri='{base}/{obj}'.format(base=baseUri,obj=obj)
	allObjects=s.get(uri).json()
	for obj in allObjects:
		if obj['name'].upper() == name.upper():
			return obj
	return None

def get_obj_from_id(s,baseUri,obj,id):
	uri='{base}/{obj}/{id}'.format(base=baseUri,obj=obj,id=id)
	r = s.get(uri)
	return r.json()

def get_resp_from_id(s,baseUri,obj,id):
	uri='{base}/{obj}/{id}'.format(base=baseUri,obj=obj,id=id)
	r = s.get(uri)
	return r

def wait_for_job(s,joburi):
	while True:
		time.sleep(1)
		job=s.get(joburi).json()
		if job['summaryDone']:
			print '{name}: {runState}'.format(name=job['name'], runState=job['jobRunState'])
			if job['jobRunState'].upper() == 'FAILURE':
				#raise Exception('Submit Job failed: {error}'.format( error=json.dumps(job['error'], indent=2) ))
				raise Exception('\nJob failed: \n{error}'.format( error=json.dumps(job, indent=2) ))
			elif job['jobRunState'].upper() == 'SUCCESS':
				return job
				break
			else:
				break

def renameVm(s,baseUri,vmId,vmNewName):
	# deprecated:  use changeVm(s,baseUri,vmId,"name",value) instead
	print "renameVm called"
	uri='{base}/Vm/{vmId}'.format(base=baseUri,vmId=vmId);
	obj=s.get(uri).json()

	debug.prt ( "VM Before Rename"                                               )
	debug.prt ( "==============================================================" )
	debug.prt ( "Name = {}".format(obj['name'])                                  )
	debug.prt ( json.dumps(obj['id'], indent=2)                  )
	debug.prt ( "==============================================================" )

	# rename in the json object
	obj['id']['name']=vmNewName
	obj['name']=vmNewName

	debug.prt ( "JSON Block After Rename"                                        )
	debug.prt ( "==============================================================" )
	debug.prt ( "Name = {}".format(obj['name'])                                  )
	debug.prt ( json.dumps(obj['id'], indent=2)                  )
	debug.prt ( "==============================================================" )

	print "Rename URI and data....."
	print "===================="

	r=s.put(uri,data=json.dumps(obj))
	job=r.json()

	if "errorCode" not in job:
		jobResult=wait_for_job(s,job['id']['uri'])
		if jobResult['jobSummaryState'] == 'SUCCESS':
			print
			print "Renaming successful"
	else:
		raise Exception('Submit Job failed: {error}'.format( error=json.dumps( job, indent=2 )))

#  end of renameVm() ------------------------------


def changeVm(s,baseUri,vmId,attribute,value):
	'''
		Attributes that can be changed:
	'''
	supportedVmAttributeChanges = [
			"name"
			,"description"
			,"cpuCount"
			,"cpuCountLimit"
			,"cpuPriority"
			,"cpuUtilizationCap"
			,"highAvailability"
			,"hugePagesEnabled"
			,"keymapName"
			,"memory"
			,"memoryLimit"
			,"networkInstallPath"
			,"osType"
			,"vmMouseType"
			,"vmStartPolicy"
			,"restartActionOnCrash"
	]

	# check that attribute is in supportedVmAttributeChanges
	try:
		i = supportedVmAttributeChanges.index(attribute)
	except ValueError as e:
		print "ERROR: changeVm attribute {} is not supported ".format(attribute)

	print "changeVm {} {} called".format(attribute,value)
	uri='{base}/Vm/{vmId}'.format(base=baseUri,vmId=vmId);
	vmObj=s.get(uri).json()

	debug.prt ( "VM Before change"                                               )
	debug.prt ( "==============================================================" )
	debug.prt ( json.dumps(vmObj, indent=2)                  )
	debug.prt ( "==============================================================" )

	# rename in the json vmObject
	if attribute == "name":
		if vmObj['id']['name'] != value and vmObj['name'] != value:
			vmObj['id']['name']=value
			vmObj['name']=value
		else:
			print "Nothing to change, {} => {} is already set".format(attribute,value)
			return
		
	else:
		if vmObj[attribute] != value:
			vmObj[attribute]=value
		else:
			print "Nothing to change, {} => {} is already set".format(attribute,value)
			return		

	debug.prt ( "VM block changed to"                                               )
	debug.prt ( "==============================================================" )
	debug.prt ( json.dumps(vmObj, indent=2)                  )
	debug.prt ( "==============================================================" )

	r=s.put(uri,data=json.dumps(vmObj))
	job=r.json()

	if "errorCode" not in job:
		jobResult=wait_for_job(s,job['id']['uri'])
		if jobResult['jobSummaryState'] == 'SUCCESS':
			print
			print "Change successful"
	else:
		raise Exception('Submit Job failed: {error}'.format( error=json.dumps( job, indent=2 )))

	vmObj=s.get(uri).json()
	debug.prt ( "VM After change"                                        )
	debug.prt ( "==============================================================" )
	debug.prt ( json.dumps(vmObj, indent=2)                  )
	debug.prt ( "==============================================================" )

#  end of changeVm() ------------------------------


def cloneVm(s,baseUri,templateVm,vmName):
	# Usage: cloneVm(s,baseUri,'OVM_OL7U5_X86_64_12102DBRAC_PVHVM-1of2.tar.gz' ,'racnode.0')
	repo_id     = myConfig['repositoryId']
	sp_id       = myConfig['serverPoolId']
	template_id = myConfig['templateNameId']

	print 'cloning template {} into VM {} repo_id {:20} ServerPool Id {}'.format(myConfig['templateName'],vmName,repo_id,sp_id)

	uri='{base}/Vm/{vmId}/clone?{repo}&{serPool}&{template}'.format(base=baseUri
																	,vmId=template_id
																	,repo='repositoryId='+repo_id
																	,serPool='serverPoolId='+sp_id
																	,template='createTemplate='+template_id
																	)
	job=s.put(uri).json()
	if "errorCode" not in job:
		# wait for the job to complete
		jobResult=wait_for_job(s,job['id']['uri'])
	else:
		raise Exception('Submit Job failed: {error}'.format( error=json.dumps( job, indent=2 )))


	debug.prt ( "JOB Object:"                                                    )
	debug.prt ( "==============================================================" )
	debug.prt ( json.dumps(jobResult, indent=2)                                  )
	debug.prt ( "==============================================================" )

	if jobResult['jobSummaryState'] == 'SUCCESS':
		clonedVmId=jobResult['resultId']['value']
		clonedVmName=jobResult['resultId']['name']
		print "Template cloned to {}".format(clonedVmName)
		print "Renaming to {}".format(vmName)
		print "=============================================================="
		print
		#renameVm(s,baseUri,clonedVmId,vmName)
		changeVm(s,baseUri,clonedVmId,"name",vmName)
		#return clonedVmId
		return get_obj_from_id(s,baseUri,'Vm',clonedVmId)
	else:
		raise Exception('Clone failed: see above error')
#  end of cloneVm() ------------------------------


def getSharable(s,baseUri, asmDiskObj):
	debug.prt ( "getSharable called " )
	id = asmDiskObj["id"]["value"]
	uri='{base}/StorageElement/{id}'.format(base=baseUri, id=id)
	r=s.get(uri).json()
	debug.prt ( "r[shareable] " + str(r["shareable"]) )
	return r["shareable"]
# end of getSharable() ------------------------------


def setSharable(s,baseUri,asmDiskObj):
	debug.prt ( "setSharable called " )
	asmDiskObj["shareable"] = True

	id = asmDiskObj["id"]["value"]
	uri='{base}/StorageElement/{id}'.format(base=baseUri, id=id)
	job=s.put(uri, data=asmDiskObj).json()
	if "errorCode" not in job:
		jobResult=wait_for_job(s,job['id']['uri'])
	else:
		raise Exception('Submit Job failed\n{uri}\nwith data\n{jobData}\nFailed with Error:\n {error}'.format( uri=uri
																				 ,jobData=json.dumps( asmDiskObj, indent=2 )
																				 ,error=json.dumps( job, indent=2 ))
																				)

	if jobResult['jobSummaryState'] == 'SUCCESS':
		return
	else:
		print ( "JOB Failed:"                                                    )
		print ( "==============================================================" )
		print ( json.dumps(jobResult, indent=2)                                  )
		print ( "==============================================================" )
		raise Exception('see above error')
# end of setSharable() ------------------------------


def setPhysicalDiskSharable(s,baseUri,asmDisk):
	print "=============================================================="
	print "setPhysicalDiskSharable called "

	asmDiskName = asmDisk["name"]
	asmDiskObj  = None
	if asmDisk["diskType"].upper() == "PHYSICAL_DISK":
		diskWwid = asmDisk["wwid"]
		if not diskWwid:
			raise Exception ("{asmDiskName} is set as Physical but the wwid is null".format(asmDiskName=asmDiskName))
		asmDiskObj=getDiskObjByWwid(s,baseUri,diskWwid)
	else:
		raise Exception ("setPhysicalDiskSharable() Usage error:  disk {disk} inappropriate disk type: {type}".format(disk=asmDiskName, type=asmDisk["diskType"] ))

	sharable = getSharable(s,baseUri, asmDiskObj)

	if sharable == True:
		print "{disk} was already sharable".format(disk=asmDiskName)
		return
	else:
		print "\nWARNING\n{disk} is not shareable and setSharable() is not working, so you need to do this manually....".format(disk=asmDiskName)
		#setSharable(s,baseUri,asmDiskObj)
		return

# end of setPhysicalDiskSharable() ------------------------------


def createVmDisk(s,baseUri,asmDisk):

	print "=============================================================="
	print "createVmDisk called to create {} {}".format(asmDisk["diskType"], asmDisk["name"])
	if asmDisk["diskType"].upper() == "PHYSICAL_DISK":
		print "Physical Disk specified, so ensuring its sharable".format(name=asmDisk["name"])
		print "setPhysicalDiskSharable is not working... if shared disks are not sharable you will get an error later...."
		#setPhysicalDiskSharable(s,baseUri,asmDisk)
		# NEED TO RETURN STORAGLE ELEMENT HERE ?????
		wwid=asmDisk["wwid"]
		#asmDisk["StorageElement"]=getDiskObjByWwid(s,baseUri,wwid)
		return getDiskObjByWwid(s,baseUri,wwid)

	# where to create disk:
	# using myConfig['repositoryIdObj'] is default, but is over-ridded by "repositoryId" in ASM disk definition

	repositoryIdObj = None
	repositoryId    = None
	diskConfigRepositoryName = asmDisk.get("repository")

	if diskConfigRepositoryName is None or diskConfigRepositoryName == "":
		# Use global / default repo
		repositoryId    = myConfig['repositoryId']
		repositoryIdObj = myConfig['repositoryIdObj']
		print "No explict repository found in disk config for {disk} so using {repo}".format(disk=asmDisk["name"], repo=myConfig['repository'])

	else:
		# use one defined in the disk's config
		repositoryId    = get_id_from_name(s,baseUri,'Repository', diskConfigRepositoryName)
		repositoryIdObj = get_idObj_from_name(s,baseUri,'Repository', diskConfigRepositoryName)
		print "Creating {disk} in {repo}".format(disk=asmDisk["name"],repo=diskConfigRepositoryName)

	print ( json.dumps(asmDisk, indent=2) )
	print "=============================================================="

	uri='{base}/Repository/{repo}/VirtualDisk?{sparse}'.format(base=baseUri
															  ,repo=repositoryId
															  ,sparse='sparse='+asmDisk['sparse']
															  )
	obj = {
		   "userData": [],
		   "locked": False,
		   "description": "{} for nodes {}".format(asmDisk['description'],myConfig['nodeList']),
		   "generation": 0,
		   "importFileName": None,
		   "diskType": "VIRTUAL_DISK",
		   "onDiskSize": None,
		   "readOnly": False,
		   "shareable": asmDisk['shareable'],
		   "absolutePath": None,
		   "vmDiskMappingIds": None,
		   "path": None,
		   "resourceGroupIds": None,
		   "mountedPath": None,
		   "size": int(asmDisk['size']) * 1024 * 1024 * 1024,
		   "assemblyVirtualDiskId": None,
		   "id": None,
		   "repositoryId": repositoryIdObj,
		   "name": asmDisk['name']
		 }

	debug.prt ( "createVmDisk uri + data:"                                       )
	debug.prt ( "==============================================================" )
	debug.prt ( uri                                                              )
	debug.prt ( json.dumps(obj, indent=2)                                        )
	debug.prt ( "==============================================================" )

	r=s.post(uri,data=json.dumps(obj))
	job=r.json()

	if "errorCode" not in job:
		jobResult=wait_for_job(s,job['id']['uri'])
		if jobResult['jobSummaryState'] == 'SUCCESS':
			print
			print "jobResult Object:"
			print "=============================================================="
			debug.prt ( json.dumps(jobResult, indent=2) )
			diskId=jobResult['resultId']['value']
			print "Disk ID {}".format(diskId)
			print "=============================================================="
			diskObj = get_obj_from_id(s,baseUri,'VirtualDisk',diskId)
			#print json.dumps(diskObj,indent=2)
			return diskObj
		else:
			print ( "JOB Failed:"                                                    )
			print ( "==============================================================" )
			print ( json.dumps(jobResult, indent=2)                                  )
			print ( "==============================================================" )
			raise Exception('see above error')
	else:
		raise Exception('Submit Job failed: {error}'.format( error=json.dumps( job, indent=2 )))

# end of createVmDisk() ------------------------------


def getDiskObjByWwid(s,baseUri,diskWwid):
	debug.prt ( ("getDiskObjByWwid called to get disk with wwid {wwid}".format(wwid=diskWwid)) )

	r=s.get(baseUri+'/StorageElement').json()
	for disk in r:
		page83Id = disk["page83Id"]
		thisWwid = page83Id[-32:]
		#print page83Id
		#print thisWwid
		if diskWwid == thisWwid:
			return disk
	raise Exception("Failed to find a disk matching wwid {wwid}".format(wwid=diskWwid))
#  end of getDiskObjByWwid() ------------------------------


def createVmDiskMapping(s,baseUri,racNode,asmDisks):
	# ------------------------------------------------------------------------------
	#
	#			create VmDiskMapping
	#
	# ------------------------------------------------------------------------------
	#
	# racNodeObj is the json node object - the whole definition
	# asmDisks is the list of disks

	# Update node's config in state file
	racNodeName = racNode['name']
	racNodeObj=get_obj_from_name(s,baseUri,"Vm",racNodeName)
	conf.save(myConfig)

	racNodeId  = racNodeObj['id']['value']

	print "=============================================================="
	print "createVmDiskMapping called to map disks for {vm} {id}".format(vm=racNodeName,id=racNodeId)
	print "=============================================================="


	# get current disk mappings
	vmDiskMappingIds = racNodeObj['vmDiskMappingIds']
	diskTarget = len(vmDiskMappingIds) - 1

	asmDiskObj  = None
	asmDiskName = None
	for asmDisk in asmDisks:
		print
		print "createVmDiskMapping mapping disk {}".format(asmDisk["name"])
		print "------------------------------------------------------------"
		#
		# if disk creation was skipped or the disks are Physical, asmDisk["obj"] will be null
		#
		if asmDisk.get("obj") is None or asmDisk["diskType"] == "PHYSICAL_DISK":
			# get the disk obj
			if asmDisk["diskType"].upper() == "PHYSICAL_DISK":
				diskWwid = asmDisk["wwid"]
				if not diskWwid:
					raise Exception ("{asmDiskName} is set as Physical but the wwid is null".format(asmDiskName=asmDisk["name"]))
				asmDiskObj=getDiskObjByWwid(s,baseUri,diskWwid)
			elif asmDisk["diskType"].upper() == "VIRTUAL_DISK":
				raise Exception ("{asmDiskName} is set as Virtual but the id is null - did you skip disk creation?".format(asmDiskName=asmDisk["name"]))
			else:
				raise Exception ("Unsupported diskType {diskType}".format(diskType=asmDisk["diskType"]))
		else:
			asmDiskObj  = asmDisk["obj"]
			asmDiskName = asmDisk["name"]

		debug.prt ( "==============================================================" )
		debug.prt ( "Disk Name: {}".format(asmDiskName)                              )
		debug.prt ( "DISK Obj:"                                                      )
		debug.prt ( json.dumps(asmDiskObj, indent=2)                                 )
		debug.prt ( "==============================================================" )

		diskId = asmDiskObj['id']['value']
		diskTarget += 1

		storageElementId = None
		virtualDiskId    = None
		if asmDisk["diskType"].upper() == "PHYSICAL_DISK":
			storageElementId = asmDiskObj['id']
		else:
			virtualDiskId = asmDiskObj['id']

		obj = {
			"userData": [],
			"locked": False,
			"description": "mapping for {racNode}".format(racNode=racNodeName),
			"generation": 1,
			"storageElementId": storageElementId,
			"vmId": racNodeObj['id'],
			"diskWriteMode": "READ_WRITE",
			"readOnly": False,
			"emulatedBlockDevice": False,
			"virtualDiskId": virtualDiskId,
			"resourceGroupIds": [],
			"diskTarget": diskTarget,
			"id": None,
			"name": "Mapping for disk Id ({diskId})".format(diskId=diskId)
		}

		uri='{base}/Vm/{vmId}/VmDiskMapping'.format(base=baseUri, vmId=racNodeId)

		debug.prt ( "uri + element: VmDiskMapping "                                  )
		debug.prt ( "==============================================================" )
		debug.prt ( uri                                                              )
		debug.prt ( json.dumps(obj, indent=2)                                        )
		debug.prt ( "==============================================================" )

		r=s.post(uri,data=json.dumps(obj))
		job=r.json()

		if "errorCode" not in job:
			jobResult=wait_for_job(s,job['id']['uri'])
			if jobResult['jobSummaryState'] == 'SUCCESS':
				print
				print "{disk} Mapping Created".format(disk=jobResult['id']['name'])
				racNodeObj=get_obj_from_name(s,baseUri,"Vm",racNodeName)
				conf.save(myConfig)
			else:
				print ( "JOB Failed:"                                                    )
				print ( "==============================================================" )
				print ( json.dumps(jobResult, indent=2)                                  )
				print ( "==============================================================" )
				raise Exception('see above error')
		else:
			raise Exception('Submit Job failed: {error}'.format( error=json.dumps( job, indent=2 )))



#  end of createVmDiskMapping() ------------------------------


def createDeployclusterConfigFile(deployclusterNetConfigFile):
	# create the netconfig file used by deploycluster

	'''
		Map json to deploycluster INI file, example:

		"name":	       "racnode0"       ->    NODE1=racnode0
		"public ip":   "192.168.1.231"  ->    NODE1IP=192.168.1.231
		"priv":        "racnode0-priv"  ->    NODE1PRIV=racnode0-priv
		"privip":      "10.10.10.231"   ->    NODE1PRIVIP=10.10.10.231
		"vip":         "racnode0-vip"   ->    NODE1VIP=racnode0-vip
		"vipip":       "192.168.1.232"  ->    NODE1VIPIP=192.168.1.233
	'''

	nodeNum=0
	iniFile=open(deployclusterNetConfigFile, "w")
	for racnode in myConfig["racnodes"]:
		nodeNum+=1
		iniFile.write("NODE{}={}\n".format(       nodeNum,racnode["name"]   ))
		iniFile.write("NODE{}IP={}\n".format(     nodeNum,racnode["public ip"]     ))
		if racnode.get("priv") is not None:
			iniFile.write("NODE{}PRIV={}\n".format(   nodeNum, racnode.get("priv")   ))

		if racnode.get("privip") is not None:
			iniFile.write("NODE{}PRIVIP={}\n".format(   nodeNum, racnode.get("privip")   ))

		if racnode.get("vip") is not None:
			iniFile.write("NODE{}VIP={}\n".format(   nodeNum, racnode.get("vip")   ))

		if racnode.get("vipip") is not None:
			iniFile.write("NODE{}VIPIP={}\n".format(   nodeNum, racnode.get("vipip")  ))

	for key in myConfig["racCommonData"]:
		iniFile.write("{}={}\n".format(key,myConfig["racCommonData"][key]))

	if args.singleInstanceHA:
		iniFile.write("CLONE_SINGLEINSTANCE_HA=yes")


	iniFile.close()
#  end of createDeployclusterConfigFile() ------------------------------

def createNodes(s,baseUri):
	# ------------------------------------------------------------------------------
	#
	#			create Vms - clone from template
	#
	# ------------------------------------------------------------------------------
	#

	if myConfig["racCommonData"].get("SCANIP") is not None:
		print "Checking IP address setting for SCANIP in config {}".format(args.configFile)
		if myConfig["racCommonData"]["SCANIP"] == "getIpAddress":
			print "\"getIpAddress\" is set\nBooking IP address"
			try:
				ip=ipAddressPkg.bookIP("For {racnodes} {ipType}".format(racnodes=myConfig["nodeList"], ipType="SCAN IP"))
				myConfig["racCommonData"]["SCANIP"]=ip
			except Exception as e:
				print "ipAddressPkg.bookIP FAILED: {}".format(e)
				exit(1)

		print "SCAN ip => " + myConfig["racCommonData"]["SCANIP"]

	for racnode in myConfig['racnodes']:
		for ipType in [ "public ip", "vipip" ]:
			if racnode.get(ipType) is not None:
				print "Checking IP address setting for {} in config {}".format(ipType, args.configFile)
				if racnode[ipType] == "getIpAddress":
					print "\"getIpAddress\" is set\nBooking IP address"
					try:
						ip=ipAddressPkg.bookIP("For {racnode} {ipType}".format(racnode=racnode["name"], ipType=ipType))
						racnode[ipType]=ip
						print ip
					except Exception as e:
						print "ipAddressPkg.bookIP FAILED: {}".format(e)
						exit(1)
				else:
					print "{} => {} ".format(ipType, racnode[ipType])

		# clone VM
		racnode['obj']=cloneVm(s, baseUri, myConfig['templateName'], racnode['name'])

		conf.save(myConfig)
		# update VM if it has nodeConfig
		if racnode.get("nodeConfig") is not None:
			nodeConfig = racnode.get("nodeConfig")
			for attribute in nodeConfig:
				value = nodeConfig[attribute]
				print "Setting {} => {}".format(attribute,value)
				try:
					vmId=racnode["obj"]["id"]["value"]
					changeVm(s,baseUri,vmId,attribute,value)
				except Exception as e:
					print "WARNING:  failed : {}".format(e)
	debug.prt ( "Node Config:" )
	debug.prt ( json.dumps(myConfig['racnodes'], indent=2) )

#  end of createNodes() ------------------------------

# def createDisks(s,baseUri):
# 	print "\n\n\nDO NOT USE createDisks() - use createDisksAndMapping instead!!!!\n\n\n"
# 	#
# 	# ------------------------------------------------------------------------------
# 	#
# 	#			create VirtualDisks
# 	#
# 	# ------------------------------------------------------------------------------
# 	#
# 	for racnode in myConfig['racnodes']:
# 		if racnode.get("localDisks") is not None:
# 			localDisks=racnode.get("localDisks")
# 			for localDisk in localDisks:
# 				localDisk['obj']=createVmDisk(s,baseUri,localDisk)
# 			conf.save(myConfig)
# 
# 			debug.prt ( "Local Disk Config for {}:".format(racnode["name"]))
# 			debug.prt ( json.dumps(localDisks, indent=2) )
# 
# 
# 	asmDisks=myConfig.get("asmDisks")
# 	if len(asmDisks) > 0:
# 		for asmDisk in asmDisks:
# 			asmDisk['obj']=createVmDisk(s,baseUri,asmDisk)
# 		conf.save(myConfig)
# 
# 		debug.prt ( "ASM Disk Config:" )
# 		debug.prt ( json.dumps(myConfig['asmDisks'], indent=2) )
# 
# 
# #  end of createDisks() ------------------------------

def createDisksAndMapping(s,baseUri):
	#
	# ------------------------------------------------------------------------------
	#
	#			for each node, create local Disks and then Mapping
	#
	# ------------------------------------------------------------------------------
	#
	for racnode in myConfig['racnodes']:
		disksToBeMapped = []
		if racnode.get("localDisks") is not None:
			localDisks=racnode.get("localDisks")
			for localDisk in localDisks:
				localDisk['obj']=createVmDisk(s,baseUri,localDisk)
				disksToBeMapped.append(localDisk)
			createVmDiskMapping(s,baseUri,racnode,disksToBeMapped)
			conf.save(myConfig)

	#
	# ------------------------------------------------------------------------------
	#
	#		 create shared / ASM Disks and Mapp to each node
	#
	# ------------------------------------------------------------------------------
	#
	if myConfig.get("asmDisks") is not None:
		asmDisks=myConfig.get("asmDisks")
		disksToBeMapped = []
		for asmDisk in asmDisks:
			# createVmDisk will return None if asm disk is Physical createVmDiskMapping() deals with that 
			#print json.dumps(asmDisk,indent=2)
			asmDisk['obj']=createVmDisk(s,baseUri,asmDisk)
			disksToBeMapped.append(asmDisk)
			conf.save(myConfig)

		for racnode in myConfig['racnodes']:
			createVmDiskMapping(s,baseUri,racnode,disksToBeMapped)
			conf.save(myConfig)


#  end of createDisks() ------------------------------

#def createDiskMappings(s,baseUri):
#	print "\n\n\nDO NOT USE createDiskMappings() - use createDisksAndMapping instead!!!!\n\n\n"
#	# ------------------------------------------------------------------------------
#	#
#	#			create VmDiskMappings
#	#
#	# ------------------------------------------------------------------------------
#
#	asmDisks=myConfig.get("asmDisks")
#	if len(asmDisks) > 0:
#		for node in myConfig['racnodes']:
#			racNodeName = node['name']
#			racNodeObj = node['obj']
#			createVmDiskMapping(s,baseUri, racNodeObj['obj'], myConfig['asmDisks'])
#			# update racnode obj as the node's diskTargets will have changed
#			node["obj"]=get_obj_from_name(s,baseUri,"Vm",racNodeName)
#			conf.save(myConfig)
#
#	for racnode in myConfig['racnodes']:
#		if racnode.get("localDisks") is not None:
#			localDisks=racnode.get("localDisks")
#			racNodeName = node['name']
#			racNodeObj = node['obj']
#			createVmDiskMapping(s,baseUri, racNodeObj['obj'], localDisks)
#
#			# update racnode obj as the node's diskTargets will have changed
#			node["obj"]=get_obj_from_name(s,baseUri,"Vm",racNodeName)
#			conf.save(myConfig)
#
## end of createDiskMappings() ------------------------------

def deleteDiskMapping(s,baseUri,m):
	print "deleteDiskMapping called"
	if len(m) == 0:
		print "no disk mapping found"
		return
	for mapping in m:
		vmName          = mapping["vmName"]
		vmId            = mapping["vmId"]
		VmDiskMapping   = mapping["mappingId"]
		virtualDiskName = mapping.get("virtualDiskName")
		if virtualDiskName is not None:
			mappedObjId = mapping["virtualDiskName"]
		else:
			mappedObjId = mapping["storageElementName"]

		print "Deleting mapping from vm {vmName} to {mappedObjId}...".format(vmName=vmName,mappedObjId=mappedObjId )
		uri='{base}/Vm/{vmId}/VmDiskMapping/{VmDiskMapping}'.format(
													base=baseUri,
													vmId=vmId,
													VmDiskMapping=VmDiskMapping)
		job=s.delete(uri).json()
		if "errorCode" not in job:
			jobResult=wait_for_job(s,job['id']['uri'])
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


def getRepositoryIdForDisk(s,baseUri,diskId):
	debug.prt ( "getRepositoryIdForDisk called" )
	uri='{base}/VirtualDisk/{diskId}'.format(base=baseUri, diskId=diskId)
	r=s.get(uri).json()

	#print json.dumps(r, indent=2)

	repositoryId=r["repositoryId"]["value"]
	return repositoryId
# end of getRepositoryIdForDisk() ------------------------------


def deleteDisks(s,baseUri,diskToBeDeletedMap):
	print "deleteDisks called..."

	if len(diskToBeDeletedMap) == 0:
		print "no disks found"
		return
	for diskId in diskToBeDeletedMap.keys():
		diskName=diskToBeDeletedMap[diskId]
		print "Deleting {} {}".format(diskId,diskName)
		RepositoryId=getRepositoryIdForDisk(s,baseUri,diskId)
		uri='{base}/Repository/{RepositoryId}/VirtualDisk/{diskId}'.format(base=baseUri,
																		   RepositoryId=RepositoryId,
																		   diskId=diskId)
		job=s.delete(uri).json()
		if "errorCode" not in job:
			jobResult=wait_for_job(s,job['id']['uri'])
			if jobResult['jobSummaryState'] == 'SUCCESS':
				print
				print "Deleted"
		else:
			raise Exception('Submit Job failed: {error}'.format( error=json.dumps( job, indent=2 )))


# end of deleteDisks() ------------------------------

def getDiskMappingsForVm(s,baseUri):
	diskMap = []
	for racnode in myConfig['racnodes']:
		vmObj = racnode.get("obj")
		if vmObj is None:
			print "No node object for {}".format(racnode["name"])
			break
		vmId = vmObj["id"]["value"]
		vmName = vmObj["id"]["name"]
		uri='{base}/VmDiskMapping'.format(base=baseUri)
		r=s.get(uri).json()
		for mapping in r:
			thisVmId = mapping["vmId"]["value"]
			if vmId == thisVmId:

				storageElementName = None
				storageElementId   = None
				virtualDiskName    = None
				virtualDiskId      = None

				if mapping.get("storageElementId") is not None:
					storageElementName = mapping["storageElementId"]["name"]
					storageElementId   = mapping["storageElementId"]["value"]
				if mapping.get("virtualDiskId") is not None:
					virtualDiskName = mapping["virtualDiskId"]["name"]
					virtualDiskId   = mapping["virtualDiskId"]["value"]
				mappingName     = mapping["id"]["name"]
				mappingId       = mapping["id"]["value"]


				diskMap.append( {
					"vmId":				   vmId,
					"vmName":			   vmName,
					"virtualDiskName":	   virtualDiskName,
					"virtualDiskId":	   virtualDiskId,
					"virtualDiskName":	   virtualDiskName,
					"storageElementName":  storageElementName,
					"storageElementId":	   storageElementId,
					"mappingName":		   mappingName,
					"mappingId":		   mappingId
				} )
	return diskMap
# end of getDiskMappingsForVm() ------------------------------

def createDiskToBeDeletedMap(m):
	d = {}
	#print json.dumps(m, indent=2)
	for virtualDiskId in m:
		if virtualDiskId["virtualDiskId"] is not None:
			virtualDiskId["virtualDiskName"]
			d.update( { virtualDiskId["virtualDiskId"] : virtualDiskId["virtualDiskName"] } )
	return d
# end of createDiskToBeDeletedMap() ------------------------------

def stopNode(obj):
	vmId=obj["id"]["value"]
	vmName=obj["id"]["name"]
	uri='{base}/Vm/{vmId}'.format(base=baseUri,vmId=vmId)
	r=s.get(uri).json()
	print "StopNode called for {vmName}".format(vmName=vmName)
	debug.prt ( "Vm as Object:" )
	debug.prt ( json.dumps(r,indent=2) )

	currentState = r.get("vmRunState")
	print "Current State: {} ".format(currentState)
	if currentState == "RUNNING":
		print "Stopping..."
		uri='{base}/Vm/{vmId}/stop'.format(base=baseUri,vmId=vmId)
		job=s.put(uri).json()
		if "errorCode" not in job:
			jobResult=wait_for_job(s,job['id']['uri'])
			if jobResult['jobSummaryState'] == 'SUCCESS':
				print
				print "{vmName} stopped".format(vmName=vmName)
		else:
			raise Exception('Submit Job failed: {error}'.format( error=json.dumps( job, indent=2 )))
	else:
		print "Nothing to do"
# end of stopNode() ------------------------------


def stopNodes():
	for racnode in myConfig['racnodes']:
		node=racnode["name"]
		print "Stop {} ".format(node)
		obj = racnode.get("obj")
		if obj is None:
			#{
			#  "obj": null,
			#  "name": "racphys1",
			#  "public ip": "getIpAddress",
			#  "vip": "racnode1-vip",
			#  "vipip": "getIpAddress",
			#  "privip": "192.168.1.11",
			#  "priv": "racnode1-priv"
			#}
			print "No node OVM object for {}".format(node)
			debug.prt ( json.dumps(racnode, indent=2) )
		else:
			stopNode(obj)

# end of stopNodes() ------------------------------

def releaseIPAddress(ip):
	try:
		ipAddressPkg.releaseIP(ip)
	except Exception as error:
		raise Exception ( "releaseIPAddress({ip}) error: {error}".format(ip, json.dumps(error, indent=2)) )
# end of releaseIPAddress() ------------------------------

def releaseIPAddresses():
	print "releaseIPAddresses( ) called..."
	for racnode in myConfig['racnodes']:
		for ipType in [ "public ip", "vipip" ]:
			if racnode[ ipType ] is not None and racnode[ ipType ] != "getIpAddress":
				try:
					print "calling releaseIPAddress({ip})...".format(ip=racnode[ ipType ])
					releaseIPAddress(racnode[ ipType ])
					racnode[ ipType ] = "getIpAddress"
				except Exception as error:
					print error

	if myConfig["racCommonData"].get("SCANIP") is not None:
		if myConfig["racCommonData"]["SCANIP"] != "getIpAddress":
			try:
				print "calling releaseIPAddress({ip})...".format( ip=myConfig["racCommonData"]["SCANIP"] )
				releaseIPAddress(  myConfig["racCommonData"]["SCANIP"] )
				myConfig["racCommonData"]["SCANIP"] = "getIpAddress"
			except Exception as error:
				print error

	conf.save(myConfig)
# end of releaseIPAddresses() ------------------------------

def deleteNode(node):
	nodeName=node["name"]
	if node["obj"] is None:
		#{
		#  "obj": null,
		#  "name": "racphys1",
		#  "public ip": "getIpAddress",
		#  "vip": "racnode1-vip",
		#  "vipip": "getIpAddress",
		#  "privip": "192.168.1.11",
		#  "priv": "racnode1-priv"
		#}
		print "deleteNode() : No node OVM object for {}".format( nodeName )
	else:
		vmId=node["obj"]["id"]["value"]
		print "deleting {nodeName}..".format(nodeName=nodeName)
		uri='{base}/Vm/{vmId}'.format(base=baseUri, vmId=vmId)
		job=s.delete(uri).json()
		if "errorCode" not in job:
			jobResult=wait_for_job(s,job['id']['uri'])
			if jobResult['jobSummaryState'] == 'SUCCESS':
				print
				print "Done"
		else:
			raise Exception('Submit Job failed: {error}'.format( error=json.dumps( job, indent=2 )))
# end of deleteNode() ------------------------------


def deleteNodes():
	for racnode in myConfig['racnodes']:
		try:
			deleteNode(racnode)
			racnode["obj"] = None
			conf.save(myConfig)
		except Exception as error:
			print error
# end of deleteNodes() ------------------------------


'''
 ======================================================================

	Start Here

 ======================================================================
'''

debug = Debug(False)

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Create n RAC nodes, single instance VM, their shared disks and mapping to all nodes")
	parser.add_argument("-v", "--verbose", action="store_true")
	parser.add_argument("-configFile", "-c", help="configuration of the build in json format", required=True)
	parser.add_argument("-paramsFile", "-p", help="deploycluster params.ini file only used for info at the moment", default="params.ini")
	parser.add_argument("-singleInstanceHA", "-single","-s", help="config deploycluster network ini file for Single instace HA",  action="store_true")

	group_ex = parser.add_mutually_exclusive_group(required=True)
	group_ex.add_argument("-apply",         help="Create RAC nodes",                                     action="store_true")
	group_ex.add_argument("-plan",          help="NOT YET IMPLEMENTED - but to be like terraform plan",  action="store_true")
	group_ex.add_argument("-destroy",       help="destroy VMs)",                                         action="store_true")

	group_ex2 = parser.add_mutually_exclusive_group()
	group_ex2.add_argument("-keepIPs",  help="used with -destroy to retain the VM IPs",           action="store_true", default=True)
	group_ex2.add_argument("-dropIPs",  help="used with -destroy to drop / release the VM IPs",   action="store_true")


	args = parser.parse_args()

	debug.setDebug(args.verbose)

	try:
		# might not be using ipAddressPkg package
		if debug.getDebug():
			print "Setting debugging in ipAddressPkg..."
			ipAddressPkg.setDebugging()
	except:
		pass

	'''
	 ------------------------------------------------------------------------------
	  load RAC configuration from initial json config file or from "state" file if it exists
	 ------------------------------------------------------------------------------
	'''

	conf = ""
	stateFileTest = os.path.splitext(args.configFile)[0] + '.state.json'

	print "\n\n\nWARNING NEW FUNCTIONALLITY TO CHECK THE STATEFILE IS NOT WORKING SO YOU MAY NEED TO DELETE THE STATEFILE YOURSELF\n\n\n"
	
	#		if args.destroy:
	#			if not os.path.isfile(stateFileTest):
	#				raise Exception("No state file found {} Nothing to destroy".format(stateFileTest))
	#			else:
	#				print "Statefile found: {}".format(stateFileTest)
	#				conf = StateFile(stateFileTest)
	#		elif os.path.isfile(stateFileTest):
	#			# chk to see if conf file is newer (has been updated) than statefile
	#			if os.path.getmtime(stateFileTest) < os.path.getmtime(args.configFile):
	#				print "\nWARNING:  config file \"{}\" is newer than generated statefile \"{}\"".format(args.configFile, stateFileTest)
	#				print "\nHave you updated \"{}\" since the last build?".format(args.configFile)
	#				print "\nEither merge your changes into the statefile or remove the statefile and try again"
	#				print "Note: if you are dynamically getting IP addesses, these will be lost if, so merge them first if you wan to keep them"
	#				exit(1)
	#			print "Found state file {} - using in preference to {}".format(stateFileTest, args.configFile)
	#			conf = StateFile(stateFileTest)
	#		else:
	#			print "No statefile found, creating {}".format(stateFileTest)
	#			copyfile(args.configFile,stateFileTest)
	#			conf = StateFile(stateFileTest)
    #		

	'''
		OLD STATEFILE LOGIC HERE

	'''
	conf = ""
	stateFileTest = os.path.splitext(args.configFile)[0] + '.state.json'
	if os.path.isfile(stateFileTest):
		print "Found state file {} - using in preference to {}".format(stateFileTest, args.configFile)
		conf = StateFile(stateFileTest)
	elif args.destroy:
		# a state file must exist to be able to run destroy as it was created duning apply
		raise Exception("No state file found {} Nothing to destroy".format(stateFileTest))
	else:
		copyfile(args.configFile,stateFileTest)
		conf = StateFile(stateFileTest)
	'''
		EOD OF OLD STATEFILE LOGIC HERE

	'''

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




	'''
	 ---------------------------------------
	  Create a Session for OVM connections
	 ---------------------------------------
	'''
	ovm_pw = None
	if myConfig.get("ovm_pw") is not None:
		ovm_pw = myConfig.get("ovm_pw")
	else:
		ovm_vault_name = myConfig.get("ovm_vault_name")
		if ovm_vault_name is not None:
			try:
				ovm_pw=passwdPkg.getOVMPasswd(ovm_vault_name,'admin')
			except Exception as e:
				print "\ngetOVMPasswd FAILED: {}".format(e)
				exit(1)
		if ovm_pw is None:
			ovm_pw = getpass.getpass("OVM admin password: ")

	s=requests.Session()
	s.auth=( myConfig['ovm_user'], ovm_pw )
	s.verify=False #disables SSL certificate verification
	s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})

	baseUri="https://{host}:{port}{uri}".format(host=myConfig["ovmHost"],
												 port=myConfig["port"],
												 uri=myConfig['baseUri'])


	'''
	 ---------------------------------------
	  Default Action = apply  i.e. Create RAC Nodes
	 ---------------------------------------
	'''

	if args.apply:

		'''
		 ---------------------------------------
		  Update RAC build configuration with repository, serverPool and template IDs...
		 ---------------------------------------
		'''

		if myConfig['repositoryId'] is None:
			print "Getting / Setting  repository, serverPool and template IDs..."
			if myConfig.get('repositoryId') is None:
				id = get_id_from_name(s,baseUri,'Repository', myConfig['repository'])
				if id is None:
					print "ERROR: could not find repositoryId {} check name and try again".format(myConfig['repository'])
					exit(1)
				myConfig['repositoryId'] = id
			if myConfig.get('repositoryIdObj') is None:
				id = get_idObj_from_name(s,baseUri,'Repository', myConfig['repository'])
				if id is None:
					print "ERROR: could not find repository {} check name and try again".format(myConfig['repository'])
					exit(1)
				myConfig['repositoryIdObj'] = id
			if myConfig.get('serverPoolId') is None:
				id = get_id_from_name(s,baseUri,'ServerPool',myConfig['serverPool'])
				if id is None:
					print "ERROR: could not find serverPool {} check name and try again".format(myConfig['serverPool'])
					exit(1)	
				myConfig['serverPoolId']    = id
			if myConfig.get('templateNameId') is None:
				id = get_id_from_name(s,baseUri,'Vm',myConfig['templateName'])
				if id is None:
					print "ERROR: could not find templateName {} check name and try again".format(myConfig['templateName'])
					exit(1)	
				myConfig['templateNameId']   = id

		if args.paramsFile is not None:
			myConfig['paramsFile']=args.paramsFile
		else:
			myConfig['paramsFile']='params.ini'


		nodeList=None;
		for n in myConfig["racnodes"]:
			if nodeList == None:
				nodeList=n["name"]
			else:
				nodeList=nodeList + "," + n["name"]
		myConfig['nodeList'] = nodeList

		debug.prt ( "myConfig" )
		debug.prt ( json.dumps(myConfig, indent=2) )
		conf.save(myConfig)

		createNodes(s,baseUri)
		conf.save(myConfig)

		# createDisks(s,baseUri)
		# createDiskMappings(s,baseUri)
		createDisksAndMapping(s,baseUri)

		#
		# Run
		#
		print
		print"===================================================================================="
		print "To complete installation, run:"
		print

		# need to integrate deploycluster.py but in the short term,....
		deploycluster="deploycluster.py"
		if not os.path.isfile(deploycluster) and os.environ["PYTHONPATH"] is not None:
			deploycluster=os.path.join(  os.environ["PYTHONPATH"],  "deploycluster.py" )
		else:
			print "Cant find deploycluster.py script"
			print "Locate its directory, copy {} cd there cd there and then run the following....".format(args.netconfig)

		# create net config files used by deploycluster
		deployclusterNetConfigFile=os.path.splitext(args.configFile)[0] + '.networkConfig.ini'
		createDeployclusterConfigFile( deployclusterNetConfigFile )

		print "python {py} --insecure -u {user} -p {pw} -H {host} -N {ini} -M {nodeList} -P {params} ".format(
																								py=deploycluster
																								,user=myConfig['ovm_user']
																								,pw=ovm_pw
																								,host=myConfig["ovmHost"]
																								,ini=deployclusterNetConfigFile
																								,nodeList=myConfig["nodeList"]
																								,params=myConfig["paramsFile"]
																							)
		print
		print"===================================================================================="
		print


		#conf.showStateFiles()
		conf.purgeOld()

		exit(0)

	# end of apply = True
	'''
	 ---------------------------------------
	  destroy  i.e. Create RAC Nodes
	 ---------------------------------------
	'''

	if args.destroy:
		print "DESTROY CALLED"

		confirm = raw_input("Please confirm that you want to DESTROY this build, type \"yes\" to confirm: ").lower()
		if confirm != "yes":
			exit(1)

		print ( "calling stopNodes()..." )
		stopNodes()

		print ( "calling getDiskMappingsForVm()..." )
		diskMap = getDiskMappingsForVm(s,baseUri)
		print ( "calling createDiskToBeDeletedMap()..." )
		diskToBeDeletedMap = createDiskToBeDeletedMap(diskMap)

		print ( "calling deleteDiskMapping()..." )
		deleteDiskMapping(s,baseUri,diskMap)
		print ( "calling deleteDisks()..." )
		deleteDisks(s,baseUri,diskToBeDeletedMap)

		if args.dropIPs or not args.keepIPs:
			print ("calling releaseIPAddresses()...")
			releaseIPAddresses()

		print ( "calling deleteNodes()..." )
		deleteNodes()

		#conf.showStateFiles()
		conf.purgeOld()


	exit(0)

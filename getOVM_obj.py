#!/usr/bin/python
#
#
#

allUris = [
 'AccessGroup'
,'AffinityGroup'
,'Assembly'
,'AssemblyVirtualDisk'
,'AssemblyVm'
,'BaseObject'
,'CloneType'
,'Cluster'
,'ClusterHeartbeatDevice'
,'ClusterStorageFs'
,'ControlDomain'
,'Cpu'
,'CpuCompatibilityGroup'
,'EthernetPort'
,'Event'
,'FileServer'
,'FileServerPlugin'
,'FileSystem'
,'FileSystemMount'
,'FsAccessGroup'
,'Id'
,'Job'
,'LoggerManagementAttributes'
,'LoginCertificate'
,'Manager'
,'Network'
,'PeriodicTask'
,'Repository'
,'RepositoryExport'
,'ResourceGroup'
,'Server'
,'ServerController'
,'ServerPool'
,'ServerPoolNetworkPolicy'
,'ServerPoolPolicy'
,'ServerUpdateConfiguration'
,'ServerUpdateRepositoryConfiguration'
,'SimpleId'
,'Statistic'
,'StorageArray'
,'StorageArrayPlugin'
,'StorageElement'
,'StorageInitiator'
,'StoragePath'
,'StorageTarget'
,'VirtualDisk'
,'VirtualNic'
,'VirtualSwitch'
,'VlanInterface'
,'Vm'
,'VmDiskMapping'
,'VmCloneDefinition'
,'VmCloneNetworkMapping'
,'VmCloneStorageMapping'
,'VolumeGroup'
,'WsErrorDetails'
,'WsException'
,'Zone'
]

uris = [
'AccessGroup',
'AffinityGroup',
'ArchiveManagement',
'Assembly',
'AssemblyVirtualDisk',
'AssemblyVm',
'BackupManagement',
'BusinessManagement',
'Certificate',
'ClusterHeartbeatDevice',
'Cluster',
'ClusterStorageFs',
'ControlDomain',
'CpuCompatibilityGroup',
'Cpu',
'EthernetPort',
'EventManagement',
'Event',
'FileServerPlugin',
'FileServer',
'FileSystemMount',
'FileSystem',
'JobManagement',
'Job',
'LogManagement',
'MacManagement',
'Manager',
'ModelManagement',
'Network',
'PeriodicTask',
'RasManagement',
'RepositoryExport',
'Repository',
'ResourceGroup',
'ServerConfiguration',
'ServerController',
'ServerPoolNetworkPolicy',
'ServerPoolPolicy',
'ServerPool',
'Server',
'ServerUpdateConfiguration',
'ServerUpdateRepositoryConfiguration',
'Statistic',
'StatisticsManagement',
'StorageArrayPlugin',
'StorageArray',
'StorageElement',
'StorageInitiator',
'StoragePath',
'StorageTarget',
'UserPreference',
'VirtualDisk',
'VirtualNic',
'VirtualSwitch',
'VlanInterface',
'VmCloneDefinition',
'VmCloneNetworkMapping',
'VmCloneStorageMapping',
'VmDiskMapping',
'Vm',
'VolumeGroup',
'Zone'
]


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

parser = argparse.ArgumentParser(description="Get json file for object passed")
parser.add_argument("-ovmConfig","-c"  ,help="OVM json config file", required=True)
parser.add_argument("-object", "-o", help="Object Name, e.g. VmDiskMapping", required=True)
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
			print "Error attempting to retrieve password from Vault: {}".format(e)
		if myConfig.get("ovm_pw") is None:
			myConfig["ovm_pw"] = getpass.getpass("OVM admin password: ")

s=requests.Session()
s.auth=( myConfig["ovm_user"], myConfig["ovm_pw"] )
s.verify=False #disables SSL certificate verification
s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
baseUri="https://{host}:{port}{uri}".format(host=myConfig["ovmHost"],
											 port=myConfig["port"],
											 uri=myConfig['baseUri'])


storageURIs = [ 'StorageArray',
				'StorageArrayPlugin',
				'StorageElement',
				'StorageInitiator',
				'StoragePath',
				'StorageTarget',
				'VirtualDisk',
				'VmDiskMapping'				]

#for uri in allUris:
#for uri in uris:

# leave as list to allow for list to be passed from command line (tbd)
objects = []
objects.append(args.object)

for uri in objects:
	print ("Getting %s Objects" % uri)
	r=s.get(baseUri+'/'+uri)
	try :
		tmpJson = r.json();
		print ("Creating / Updating {}.json".format(args.object))
		jsonFile="{}.json".format(args.object)
		with open(jsonFile,'w') as f:
			json.dump(tmpJson, f, indent=2, sort_keys=True)
		f.close()
	except :
		print json.dumps(tmpJson, indent=2, sort_keys=True)
		print("No data found for %s" % uri)



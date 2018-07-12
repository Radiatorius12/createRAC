#!/bin/python

import requests
import json
import argparse
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import getpass
try:
	import passwdPkg
except Exception as e:
	print "Warning: could not load passwdPkg : {}".format(e)
import createRACnodes


parser = argparse.ArgumentParser(description="Get the OVM name for a WWID")
parser.add_argument("-ovmConfig","-c"  ,help="OVM json config file", required=True)
parser.add_argument("-wwid",  help="wwid for the disk. Colon notation IS allowed.  If no wwid is given, all disk will be shown", default="all")
args = parser.parse_args()

try:
	with open(args.ovmConfig, "r") as f:
		myConfig = json.load(f)
except ValueError as e:
	print "The ovmConfig file \"{}\" is not valid json".format(args.ovmConfig)
	exit(1)

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
  
wwid = args.wwid.replace(':','').lower()

print "Looking for {}....".format(wwid)

r=s.get(baseUri+'/StorageElement').json()
for disk in r:
	#thisWwid = re.sub('.* \((\w*)\)', r'\1', disk["name"] , flags = re.IGNORECASE)
	#thisWwid = re.sub('\/dev\/mapper\/(\w*)', r'\1', disk["name"] , flags = re.IGNORECASE)
	#StorageElement.json:    "page83Id": "3600601600ec03600cb545b949352e811",
	#                                    ^
	page83Id = disk["page83Id"]
	thisWwid = page83Id[-32:]
	#print page83Id
	#print thisWwid
	if wwid == thisWwid or wwid == "all":
		print "OVM ID: {id} WWID : {wwid} OVM Disk: \"{ovm}\" size {size:.1f} GB shareable={shareable} description=\"{desc}\"".format(
				id=disk["id"]["value"],
				wwid=thisWwid,
				ovm=disk["name"],
				size=disk["size"] / 1024 / 1024 / 1024,
				shareable=disk["shareable"],
				desc=disk["description"]
				)




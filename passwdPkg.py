#!/bin/python

import requests
import json
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Passwd:
	myPasswd = ""

	def __init__(self,pw):
		self.myPasswd = pw

	def getPasswd(self):
		return self.myPasswd

	def setPasswd(self,pw):
		self.myPasswd = pw
	
def getPasswd(path,username):
	# ovmPath http://10.119.131.50:8200/v1/cmp   /vmm/uat_ovm
	uri='{base}/{path}'.format(base=baseUri, path=path)
	#print "uri ",uri
	r=s.get(uri).json()
	if r.get("errors"):
		raise Exception ( r["errors"] )
	d=r["data"]
	if d["username"] == username:
		return d["password"]
	return None

def getOVMPasswd(ovm_name,username):
	# ovmPath http://10.119.131.50:8200/v1/cmp/vmm/uat_ovm
	ovmPath='/vmm/{ovm_name}'.format(ovm_name=ovm_name)
	return getPasswd(ovmPath,username)

#vaultHost="10.119.131.50"
vaultHost="10.119.131.49"
vaultPort="8200"
baseVaultPath="/v1/cmp"
baseUri="https://{host}:{port}{uri}".format(host=vaultHost,
											port=vaultPort,
											uri=baseVaultPath)

'''
	Connect to Vault
'''
s=requests.Session()
s.verify=False #disables SSL certificate verification
s.headers.update({'X-Vault-Token': 'ovm-read-token'})


if __name__ == '__main__':
	ovmPasswd=Passwd(getOVMPasswd('uat_ovm','admin'))

	print ovmPasswd.getPasswd()


	







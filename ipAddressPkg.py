import requests
import json
import re
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

s=requests.Session()
s.verify=False #disables SSL certificate verification
s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
baseUri='http://10.119.131.52:3000/api'

debug=False
def setDebugging():
	debug=True

def debugPrint(s):
	if debug:
		print(s)
		
def getIP(ip):
	uri="{baseUri}/ipAddresses".format(baseUri=baseUri)
	ipList=s.get(uri).json()
	for thisIp in ipList:
		if ip == thisIp["ipAddress"]:
			return thisIp
	return None
		
def getIpId(ip):
	uri="{baseUri}/ipAddresses".format(baseUri=baseUri)
	ipList=s.get(uri).json()
	for thisIp in ipList:
		if ip == thisIp["ipAddress"]:
			return thisIp["id"]
	return None
	
		
def releaseIP(ip):
	print "releaseIP({ip}) called".format(ip=ip)
	id=getIpId(ip)
	if id is None:
		raise Exception( "{name}.releaseIP: IP address {ip} not found".format(name=__name__, ip=ip) )
		
	uri="{baseUri}/ipAddresses/{id}/release".format(baseUri=baseUri,id=id)
	r=s.put(uri).json()
	if debug:
		print json.dumps(r,indent=2)
	

def bookIP(description, networkId=1):
	# http://10.119.131.52:3000/api/networks/1/book -d '{"count":"5", "note": "Oracle RAC 2 phys disks benchmarking"}'
	uri="{baseUri}/networks/{networkId}/book".format(baseUri=baseUri,networkId=networkId)
	obj = {"count":1, "note": description}
	debugPrint(uri)
	debugPrint(obj)

	r=s.put(uri, data = json.dumps(obj)).json()
	debugPrint ( json.dumps(r,indent=2) )
	return r[0]["ipAddress"]

if __name__ == '__main__':
	setDebugging()	
	newIp=bookIP("Testing - TonyA")
	print "NewIp = " + newIp

	releaseIP(newIp)
	
	

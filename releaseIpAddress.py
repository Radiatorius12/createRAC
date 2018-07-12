#!/bin/python

import requests
import json
import re
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description="Get IP Pool addresses")
parser.add_argument("-debug",   action="store_true")
parser.add_argument("-ip",       help="Release ip Address = <IP> ", required=True)

args = parser.parse_args()

s=requests.Session()
s.verify=False #disables SSL certificate verification
s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
baseUri='http://10.119.131.52:3000/api/ipAddresses'

from ipAddressPkg import getIP
from ipAddressPkg import releaseIP

#def getIP(ip):
#	ipList=s.get(baseUri).json()
#	for ip in ipList:
#		if args.ip == ip["ipAddress"]:
#			return ip
#	return None
#
#def debugPrint(s):
#	if args.debug:
#		print(s)
#		
#def releaseIP(ip):
#	id=ip["id"]
#	uri="{baseUri}/{id}/release".format(baseUri=baseUri,id=id)
#	r=s.put(uri).json()
#	print json.dumps(r,indent=2)
	
ip = getIP(args.ip)	
print "ip = {}".format( json.dumps(ip, indent=2) )

confirm = raw_input("Please confirm that you want to release this IP, type yes to confirm: ").lower()

print type(ip)

if confirm == "yes":
	print "calling releaseIP( ip[\"{ipAddress}\"] )".format(ipAddress=ip["ipAddress"])
	releaseIP( ip["ipAddress"] )
else:
	print "Not releasing"

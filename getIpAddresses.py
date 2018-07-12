#!/bin/python

import requests
import json
import re
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description="Get IP Pool addresses")
group = parser.add_mutually_exclusive_group()
parser.add_argument("-debug",              action="store_true")
group.add_argument("-booked",       "-b", help="Show only Booked or Unavailable IPs",    action="store_true")
group.add_argument("-available",    "-a", help="Show only Available IPs",                action="store_true")
parser.add_argument("-description", "-d", help="Filter on descriptin")
parser.add_argument("-networkId",   "-n", help="Filter on networkId", type=int)
ipGroup = parser.add_mutually_exclusive_group()
ipGroup.add_argument("-ipAddressExact",   "-i", help="Filter on ip Address = <IP> ")
ipGroup.add_argument("-ipAddressMatch",   "-im", help="Filter on ip Address regexp match IP")

args = parser.parse_args()

s=requests.Session()
s.verify=False #disables SSL certificate verification
s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
baseUri='http://10.119.131.52:3000/api/ipAddresses'


def debugPrint(s):
	if args.debug:
		print(s)
		
ipList=s.get(baseUri).json()
for ip in ipList:
	ip.update({"show":0})
	if not args.booked and not args.available:
		ip["show"]=1
	elif args.booked:
		if ip["status"] == "Booked" or ip["status"] == "Unavailable":
			ip["show"]=1
	elif args.available:
		if ip["status"] == "Available":
			ip["show"]=1

	if args.description is not None and ip["show"] == 1:
		if ip["note"] is None:
			ip["show"]=0
			debugPrint ("Failed match, null description {} ".format(ip))
		else:
			if re.search(args.description, ip["note"], re.IGNORECASE) :
				ip["show"]=1
				debugPrint ("Matched: have {}  looking for {}".format(ip["note"], args.description))
			else:
				ip["show"]=0
				debugPrint ("Failed match have {}  looking for {}".format(ip["note"], args.description))

	if args.networkId is not None and ip["show"] == 1:
		if args.networkId == ip["networkId"] :
			ip["show"]=1
			debugPrint ( json.dumps(ip,indent=2) )
			debugPrint ("Matched: have {}  looking for {}".format(ip["networkId"], args.networkId))
		else:
			ip["show"]=0
			debugPrint ( json.dumps(ip,indent=2) )
			debugPrint ("Failed match have {}  looking for {}".format(ip["networkId"], args.networkId))

	if args.ipAddressMatch is not None and ip["show"] == 1:
		if re.search(args.ipAddressMatch, ip["ipAddress"], re.IGNORECASE) :
			ip["show"]=1
			debugPrint ("Matched: have {}  looking for {}".format(ip["ipAddress"], args.ipAddressMatch))
		else:
			ip["show"]=0
			debugPrint ("Failed match have {}  looking for {}".format(ip["ipAddress"], args.ipAddressMatch))

	if args.ipAddressExact is not None and ip["show"] == 1:
		if args.ipAddressExact == ip["ipAddress"]:
			ip["show"]=1
			debugPrint ("Matched: have {}  looking for {}".format(ip["ipAddress"], args.ipAddressExact))
		else:
			ip["show"]=0
			debugPrint ("Failed match have {}  looking for {}".format(ip["ipAddress"], args.ipAddressExact))

for ip in ipList:
	if ip["show"] == 1:
		print ("Status: {status}".format(status=ip["status"])                                                                )
		print ("ipAddress: {ipAddress}".format(ipAddress=ip["ipAddress"])                                                    )
		print ("networkId: {networkId}".format(networkId=ip["networkId"])                                                    )
		print ("id: {id}".format(id=ip["id"])                                                    )
		print ("description: {description}".format(description=ip["note"])                                              )
		print ("created: {createdAt} updated {updatedAt}".format(createdAt=ip["createdAt"],updatedAt=ip["updatedAt"]) )
		print
		
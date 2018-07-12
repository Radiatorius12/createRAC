import requests
import json
import argparse
import re
import time

parser = argparse.ArgumentParser(description="Get the OVM name for a WWID")
#parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-user",  help="OVM admin username", default="admin")
parser.add_argument("-pw",    help="password for admin user", required=True)
parser.add_argument("-wwid",  help="wwid for the disk. Colon notation IS allowed.  If no wwid is given, all disk will be shown", default="all")
args = parser.parse_args()


# strip ":" from wwid
wwid=args.wwid.replace(":","").lower()

s=requests.Session()
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
s.auth=(args.user, args.pw)
s.verify=False #disables SSL certificate verification
s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
# ovmmanager.uat.emiratesnbd.com=10.119.28.31
baseUri='https://10.119.28.31:7002/ovm/core/wsapi/rest'
  
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
				
def changeVmAttribute(s,baseUri,vmId,attribute, value):
	print "changeVmAttribute called"
	uri='{base}/Vm/{vmId}'.format(base=baseUri,vmId=vmId);
	
	# get existing VM config:
	obj=s.get(uri).json()

	print ( "VM Before "                                               )
	print ( "==============================================================" )
	print ( json.dumps(obj, indent=2, sort_keys=True)                  )
	print ( "==============================================================" )

	# change config
	obj[attribute]=value

	r=s.put(uri,data=json.dumps(obj))
	job=r.json()

	if "errorCode" not in job:
		jobResult=wait_for_job(s,job['id']['uri'])
		if jobResult['jobSummaryState'] == 'SUCCESS':
			print
			print "Renaming successful"
	else: 
		raise Exception('Submit Job failed: {error}'.format( error=json.dumps( job, indent=2 )))

	print ( "VM After "                                        )
	print ( "==============================================================" )
	print ( json.dumps(obj, indent=2, sort_keys=True)                  )
	print ( "==============================================================" )

#  end of renameVm() ------------------------------

attribtes=[
'name'
,'description'
,'bootOrder'
,'cpuCount'
,'cpuCountLimit'
,'cpuPriority'
,'cpuUtilizationCap'
,'highAvailability'
,'hugePagesEnabled'
,'keymapName'
,'memory'
,'memoryLimit'
,'networkInstallPath'
,'osType'
,'serverId'
,'vmDomainType'
,'vmMouseType'
,'vmRunState'
,'vmStartPolicy'
,'restartActionOnCrash'
]

#           "value": "0004fb000006000088c88f699c391fa8",

vmId="0004fb000006000088c88f699c391fa8"

changeVmAttribute(s,baseUri,vmId,"cpuCountLimit",3)
changeVmAttribute(s,baseUri,vmId,'cpuCount',2)

# "message": "OVMRU_005002E Operation not allowed- Virtual Machine: racvirt1, is not STOPPED. It is RUNNING. [Sun Jun 03 15:24:03 GST 2018]",



import os
import json
import datetime
from shutil import copyfile


class StateFile:
	oldStateFiles = []
	stateFileName = ""

	# The init method or constructor
	def __init__(self, n):
		self.stateFileName = n

	def purgeOld(self):
		for f in self.oldStateFiles:
			try:
				print "rm {}".format(f)
				os.remove(f)
			except OSError as e:
				print "Warning: failed to delete {} : {}".format(f,str(e))

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



if __name__ == '__main__':
	#stateFile = StateFile(os.path.splitext(args.configFile)[0] + '.state.json')
	stateFile = StateFile("testTestTest" + '.state.json')

	#stateFile.printStateFile
	print "getName() ", stateFile.getName()

	d = { "name": "tony test"}
	stateFile.save(d)
	stateFile.save(d)
	stateFile.save(d)
	stateFile.showStateFiles()

	stateFile.purgeOld()




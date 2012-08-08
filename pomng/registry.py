#  This file is part of pom-ng-console.
#  Copyright (C) 2012 Guy Martin <gmsoft@tuxicoman.be>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

class registry:

	def __init__(self, proxy):
		self.proxy = proxy
		self.fetch()

	def getVersion(self):
		return self.proxy.core.getVersion()

	def getClasses(self):
		return self.registry

	def getClass(self, clsName):
		return self.registry[clsName]

	def getInstance(self, cls, instName):
		if instName in cls['instances']:
			return cls['instances'][instName]
		return None

	def getProxy(self):
		return self.proxy

	def load(self, configName):
		try:
			self.proxy.registry.load(configName)
		except:
			print("Error while loading configuration '" + configName + "'")

	def save(self, fileName):
		try:
			self.proxy.registry.save(fileName)
		except:
			print("Error while saving configuration '" + configName + "'")

	def addInstance(self, objClass, objName, objType):
	
		cls = self.getClass(objClass)
		inst = self.getInstance(cls, objName)

		if not inst == None:
			print(objClass + " '" + objName + "' already exists")
			return

		try:
			self.proxy.registry.addInstance(objClass, objName, objType)
		except Exception as e:
			print("Error while adding " + objClass + " '" + objName + "' :", e)

	def setInstanceParameter(self, objClass, objName, paramName, paramValue):
		cls = self.getClass(objClass)
		inst = self.getInstance(cls, objName)

		params = inst['parameters']
		
		if not paramName in params:
			print("No parameter '" + paramName + "' in " + objClass + " '" + objName + "'")
			return

		try:
			self.proxy.registry.setInstanceParam(objClass, objName, paramName, paramValue)
		except Exception as e:
			print("Error while setting " + objClass + " '" + objName + "' parameter '" + paramName + "' to '" + paramValue + "'")


	def removeInstance(self, objClass, objName):
		try:
			self.proxy.registry.removeInstance(objClass, objName)
		except Exception as e:
			print("Error while removing " + objClass + " '" + objName + "' :", e)

	def nameMap(self, lst):
	
		res = {}
		for item in lst:
			res[item['name']] = {}
			resItem = res[item['name']]
			for key in item:
				if key == 'name':
					continue
				resItem[key] = item[key]
		return res

	def fetch(self):
		# This fetchs the classes in a more python way
		reg = self.proxy.registry.list()
		res = self.nameMap(reg['classes'])
		for cls in res:
			instances = []
			for inst in res[cls]['instances']:
				instances.append(self.proxy.registry.getInstance(cls, inst['name']))
			res[cls]['instances'] = self.nameMap(instances)
			
			# update the parameters
			instances = res[cls]['instances']
			for inst in instances:
				instances[inst]['parameters'] = self.nameMap(instances[inst]['parameters'])

		self.registry = res

	def update(self, proxy=None):
		
		if proxy == None:
			proxy = self.proxy
		oldReg = self.registry
		newReg = self.nameMap(proxy.registry.list()['classes'])

		# for each class, check if everything matches
		for cls in oldReg:

			oldCls = oldReg[cls]
			newCls = newReg[cls]

			# Serial for this class changed !
			if oldCls['serial'] != newCls['serial']:

				print("Found changes in class " + cls)

				# Check if instances were added or removed
				oldInst = oldCls['instances']
				newInst = self.nameMap(newCls['instances'])

				# Check for added instances
				addedInst = set(newInst.keys()) - set(oldInst.keys())
				if len(addedInst) > 0:
					for added in addedInst:
						print(cls + " '" + added + "' added")
						newInstance = proxy.registry.getInstance(cls, added)
						print(newInstance)
						newInstance['parameters'] = self.nameMap(newInstance['parameters'])	
						print(newInstance)
						oldCls['instances'].update(self.nameMap([newInstance]))
				

				# Check for removed instances
				removedInst = set(oldInst.keys()) - set(newInst.keys())
				if len(removedInst) > 0:
					for removed in removedInst:
						print(cls + " '" + removed + "' removed")
						oldCls['instances'].pop(removed)


				# Check for changed serials
				for inst in newInst:
					if newInst[inst]['serial'] != oldInst[inst]['serial']:
						oldParams = oldInst[inst]['parameters']
						changedInstance = proxy.registry.getInstance(cls, inst)
						newParams = self.nameMap(changedInstance['parameters'])
						for paramName in newParams:
							if newParams[paramName]['value'] != oldParams[paramName]['value']:
								print("Parameter of " + cls + " '" + paramName + "' changed from " + oldParams[paramName]['value'] + " to " + newParams[paramName]['value'])
								oldParams[paramName]['value'] = newParams[paramName]['value']


				oldCls['serial'] = newCls['serial']





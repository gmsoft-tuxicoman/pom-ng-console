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

	console = None

	def __init__(self, proxy):
		self.proxy = proxy
		self.fetch()
		self.classes_serial = 0
		self.configs_serial = 0

	def setConsole(self, console):
		self.console = console

	def getVersion(self):
		return self.proxy.core.getVersion()

	def getClasses(self):
		return self.registry

	def getClass(self, clsName):
		return self.registry[clsName]

	def getConfigs(self):
		return self.configs

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
			self.console.print("Error while loading configuration '" + configName + "'")

	def save(self, configName):
		try:
			self.proxy.registry.save(configName)
		except:
			self.console.print("Error while saving configuration '" + configName + "'")

	def delete_config(self, configName):
		try:
			self.proxy.registry.delete_config(configName)
		except:
			self.console.print("Error while deleting configuration '" + configName + "'")

	def addInstance(self, objClass, objName, objType):
	
		cls = self.getClass(objClass)
		inst = self.getInstance(cls, objName)

		if not inst == None:
			self.console.print(objClass + " '" + objName + "' already exists")
			return

		try:
			self.proxy.registry.addInstance(objClass, objName, objType)
		except Exception as e:
			self.console.print("Error while adding " + objClass + " '" + objName + "' : " + str(e))

	def setClassParameter(self, objClass, paramName, paramValue):
		cls = self.getClass(objClass)

		params = cls['parameters']
		
		if not paramName in params:
			self.console.print("No parameter '" + paramName + "' in " + objClass)
			return False

		try:
			self.proxy.registry.setClassParam(objClass, paramName, paramValue)
		except Exception as e:
			self.console.print("Error while setting " + objClass + " parameter '" + paramName + "' to '" + paramValue + "'")
			return False

		return True

	def setInstanceParameter(self, objClass, objName, paramName, paramValue):
		cls = self.getClass(objClass)
		inst = self.getInstance(cls, objName)

		if inst == None:
			self.console.print(objClass + " '" + objName + "' does not exists")
			return False

		params = inst['parameters']
		
		if not paramName in params:
			self.console.print("No parameter '" + paramName + "' in " + objClass + " '" + objName + "'")
			return False

		try:
			self.proxy.registry.setInstanceParam(objClass, objName, paramName, paramValue)
		except Exception as e:
			self.console.print("Error while setting " + objClass + " '" + objName + "' parameter '" + paramName + "' to '" + paramValue + "'")
			return False

		return True

	def removeInstance(self, objClass, objName):
		try:
			self.proxy.registry.removeInstance(objClass, objName)
		except Exception as e:
			self.console.print("Error while removing " + objClass + " '" + objName + "' : " + str(e))

	def getClassPerf(self, objClass, perfList):
		cls = self.getClass(objClass)
		if not cls:
			self.console.print("class '" + objClass + "' does not exists")
			return None
		if len(cls['performances']) == 0:
			return []

		perfs = []
		for perf in perfList:
			perfs.append({ 'class': objClass, 'perf': perf})

		return self.getPerfs(perfs)

	def getInstancePerf(self, objClass, instName, perfList):
		
		cls = self.getClass(objClass)
		inst = self.getInstance(cls, instName)
		if not inst:
			self.console.print(objClass + " '" + instName + "' does not exists")
			return None
		if len(inst['performances']) == 0:
			return []

		perfs = []
		for perf in perfList:
			perfs.append({ 'class': objClass, 'instance': instName, 'perf': perf})

		return self.getPerfs(perfs)

	def getPerfs(self, perfs):
		try:
			perfs = self.proxy.registry.getPerfs(perfs)
		except Exception as e:
			self.console.print("Error while retrieving performance objects " + str(e))
		perfs = self.nameMap(perfs, "perf")

		# Add useful details about each perf
		for perf in perfs:
			cls = self.getClass(perfs[perf]['class'])
			if 'instance' in perfs[perf]:
				inst = self.getInstance(cls, perfs[perf]['instance'])
				perfs[perf]['unit'] = inst['performances'][perf]['unit']
				perfs[perf]['type'] = inst['performances'][perf]['type']
			else:
				perfs[perf]['unit'] = cls['performances'][perf]['unit']
				perfs[perf]['type'] = cls['performances'][perf]['type']

		return perfs

	def resetAllPerfs(self):
		self.proxy.registry.resetAllPerfs()
		return True

	def resetClassPerfs(self, clsName):
		self.proxy.registry.resetClassPerfs(clsName)

	def resetInstancePerfs(self, clsName, instName):
		self.proxy.registry.resetInstancePerfs(clsName, instName)

	def nameMap(self, lst, key_str = "name"):
	
		res = {}
		for item in lst:
			res[item[key_str]] = {}
			resItem = res[item[key_str]]
			for key in item:
				if key == key_str:
					continue
				resItem[key] = item[key]
		return res

	def fetch(self):
		# This fetchs the classes in a more python way
		reg = self.proxy.registry.list()
		self.classes_serial = reg['classes_serial']
		self.configs_serial = reg['configs_serial']
		self.configs = reg['configs']

		res = self.nameMap(reg['classes'])
		for cls in res:
			res[cls]['parameters'] = self.nameMap(res[cls]['parameters'])
			res[cls]['performances'] = self.nameMap(res[cls]['performances'])

			instances = []
			for inst in res[cls]['instances']:
				instances.append(self.proxy.registry.getInstance(cls, inst['name']))
			res[cls]['instances'] = self.nameMap(instances)
			
			# update the parameters
			instances = res[cls]['instances']
			for inst in instances:
				instances[inst]['parameters'] = self.nameMap(instances[inst]['parameters'])
				instances[inst]['performances'] = self.nameMap(instances[inst]['performances'])

		self.registry = res

	def update(self, proxy=None):
		
		if proxy == None:
			proxy = self.proxy

		newReg = proxy.registry.list()

		if self.classes_serial != newReg['classes_serial']:

			oldClss = self.registry
			newClss = self.nameMap(newReg['classes'])

			# for each class, check if everything matches
			for cls in oldClss:

				oldCls = oldClss[cls]
				newCls = newClss[cls]

				# Serial for this class changed !
				if oldCls['serial'] != newCls['serial']:

					# Check if class parameters were changed
					oldParams = oldCls['parameters']
					newParams = self.nameMap(newCls['parameters'])
					for paramName in newParams:
						if newParams[paramName]['value'] != oldParams[paramName]['value']:
							self.console.print("Global " + cls + " parameter '" + paramName + "' changed from " + oldParams[paramName]['value'] + " to " + newParams[paramName]['value'])
							oldParams[paramName]['value'] = newParams[paramName]['value']

					# Check if instances were added or removed
					oldInst = oldCls['instances']
					newInst = self.nameMap(newCls['instances'])

					# Check for added instances
					addedInst = set(newInst.keys()) - set(oldInst.keys())
					if len(addedInst) > 0:
						for added in addedInst:
							self.console.print(cls + " '" + added + "' added")
							newInstance = proxy.registry.getInstance(cls, added)
							newInstance['parameters'] = self.nameMap(newInstance['parameters'])
							newInstance['performances'] = self.nameMap(newInstance['performances'])
							oldCls['instances'].update(self.nameMap([newInstance]))
					

					# Check for removed instances
					removedInst = set(oldInst.keys()) - set(newInst.keys())
					if len(removedInst) > 0:
						for removed in removedInst:
							self.console.print(cls + " '" + removed + "' removed")
							oldCls['instances'].pop(removed)


					# Check for changed serials
					for inst in newInst:
						if newInst[inst]['serial'] != oldInst[inst]['serial']:
							oldParams = oldInst[inst]['parameters']
							changedInstance = proxy.registry.getInstance(cls, inst)
							newParams = self.nameMap(changedInstance['parameters'])
							for paramName in newParams:
								if newParams[paramName]['value'] != oldParams[paramName]['value']:
									self.console.print("Parameter of " + cls + " '" + paramName + "' changed from " + oldParams[paramName]['value'] + " to " + newParams[paramName]['value'])
									oldParams[paramName]['value'] = newParams[paramName]['value']


					oldCls['serial'] = newCls['serial']

		if self.configs_serial != newReg['configs_serial']:
			self.configs = newReg['configs']




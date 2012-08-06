
class registry:
	

	def __init__(self, proxy):
		self.proxy = proxy
		self.load()

	def getClasses(self):
		return self.registry['classes']

	def getProxy(self):
		return self.proxy

	def addInstance(self, objClass, objName, objType):
		self.proxy.registry.addInstance(objClass, objName, objType)

	def load(self):
		self.registry = self.proxy.registry.list()
		
		# for each class, load the instances
		classes = self.registry['classes']
		for clsId in range(len(self.registry['classes'])):
			cls = classes[clsId]
			for instId in range(len(cls['instances'])):
				inst = cls['instances'][instId]
				cls['instances'][instId] = self.proxy.registry.getInstance(cls['name'], inst['name'])

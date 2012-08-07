
import xmlrpc.client
import _thread
import os
from . import registry

class pom:

	proxy = None
	logLevel = 3

	def __init__(self, url):
		self.url = url
		self.proxy = xmlrpc.client.ServerProxy(url)
		self.registry = registry.registry(self.proxy)
		self.serials = self.proxy.core.serialPoll(0)
		_thread.start_new_thread(self.pollSerial, (xmlrpc.client.ServerProxy(url), ))

	def getVersion(self):
		return self.proxy.core.getVersion()

	def setLoggingLevel(self, level):
		self.logLevel = level
	
	def getLoggingLevel(self):
		return self.logLevel
	
	def getLoggingLevels(self):
		return [ 'error', 'warning', 'info', 'debug' ]

	def updateLogs(self, proxy, logId):
		logs = proxy.core.getLog(logId)
		for log in logs:
			if log['level'] <= self.logLevel:
				print(log['data'])
			
	def pollSerial(self, pollProxy):
		while True:
			try:
				serials = pollProxy.core.serialPoll(self.serials['main'])
			except Exception as e:
				print("Error while polling pom-ng :", e)
				os._exit(1)

			if serials['registry'] != self.serials['registry']:
				self.registry.update(pollProxy)
			if serials['log'] != self.serials['log']:
				self.updateLogs(pollProxy, self.serials['log'])
			
			self.serials = serials

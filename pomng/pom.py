
import xmlrpc.client
import _thread
import os
from . import registry

class pom:

	proxy = None
	serials = { 'main' : 0, 'registry' : 0 }

	def __init__(self, url):
		self.url = url
		self.proxy = xmlrpc.client.ServerProxy(url)
		self.registry = registry.registry(self.proxy)
		_thread.start_new_thread(self.pollSerial, (xmlrpc.client.ServerProxy(url), ))

	def getVersion(self):
		return self.proxy.core.getVersion()

	def pollSerial(self, pollProxy):
		while True:
			try:
				serials = pollProxy.core.serialPoll(self.serials['main'])
			except Exception as e:
				print("Error while polling pom-ng :", e)
				os._exit(1)
			if serials['registry'] != self.serials['registry']:
				self.registry.update(pollProxy)
			self.serials = serials

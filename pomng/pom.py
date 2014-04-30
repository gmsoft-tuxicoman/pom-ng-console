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

import xmlrpc.client
import _thread
import os
import time
from . import registry

class pom:

	proxy = None
	logLevel = 3
	console = None

	def __init__(self, url):
		self.url = url
		self.proxy = xmlrpc.client.ServerProxy(url)
		self.registry = registry.registry(self.proxy)
		self.serials = { 'log' : 0, 'registry' : 0 }
		_thread.start_new_thread(self.pollRegistry, (xmlrpc.client.ServerProxy(url), ))
		self.logProxy = xmlrpc.client.ServerProxy(url)
		_thread.start_new_thread(self.pollLog, (self, ) )

	def halt(self):
		self.proxy.system.shutdown("halt command issued")

	def setConsole(self, console):
		self.console = console
		self.registry.setConsole(console)

	def getVersion(self):
		return self.proxy.core.getVersion()

	def setLoggingLevel(self, level):
		self.logLevel = level
		# Force the current transaction to restart
		try:
			self.logProxy.close();
		except:
			pass
	
	def getLoggingLevel(self):
		return self.logLevel
	
	def getLoggingLevels(self):
		return [ 'none', 'error', 'warning', 'info', 'debug' ]


	def pollLog(self, pollProxy):
		while True:
				
			if self.logLevel == 0:
				time.sleep(2)
				continue

			try:
				logs = self.logProxy.core.pollLog(self.serials['log'], self.logLevel, 100)
				for log in logs:
					self.console.print(log['data'])
					if self.serials['log'] < log['id']:
						self.serials['log'] = log['id']
			except Exception as e:
				time.sleep(1)
				continue

			
	def pollRegistry(self, pollProxy):
		failed = False
		while True:
			try:
				serial = pollProxy.registry.poll(self.serials['registry'])

				if serial < self.serials['registry']:
					self.serials['logs'] = 0;

				if serial != self.serials['registry']:
					self.registry.update(pollProxy)

				self.serials['registry'] = serial
				
			except Exception as e:
				if not failed:
					self.console.print("Error while polling pom-ng : " + str(e))
					failed = True
					self.console.setConnected(False)
				time.sleep(1)
				continue

			if failed:
				self.console.print("Polling pom-ng again. Reloading registry...")
				self.registry.fetch()
				self.console.print("Registry reloaded")
				self.console.setConnected(True)
				failed = False
				continue


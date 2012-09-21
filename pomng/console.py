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

import readline
import shlex
import sys

class console:
	
	prompt = "pom> "
	curMatch = []
	cmdSignatureMaxLen = 0
	connected = True
	cmdRunning = False

	cmdTree = {}

	def __init__(self, pom):
		self.pom = pom
		self.pom.setConsole(self)
		readline.parse_and_bind("tab: complete")
		readline.set_completer(self.complete)
		self.registerCmds([{ 'cmd' : "help", 'signature' : "help (command)", 'help' : "Display help for all or a specific command", 'callback' : self.cmdHelp, 'complete' : self.completeHelp, 'numargs' : -1 }])

	def cmdloop(self):
		while 1:
			line = input(self.prompt)

			self.cmdRunning = True

			split_line = shlex.split(line)
			if len(split_line) == 0:
				self.cmdRunning = False
				continue

			res = self.cmdMatch(shlex.split(line))
			if res == None:
				self.cmdRunning = False
				continue

			if not self.connected:
				self.print("Cannot execute command while not connected")
				self.cmdRunning = False
				continue

			callback = res[0]['callback']
			args = res[1]

			numargs = 0
			if 'numargs' in res[0]:
				numargs = res[0]['numargs']
			
			if numargs != -1 and len(args) != numargs:
				self.print("Invalid number of arguments. Expected " + str(res[0]['numargs']) + ", got " + str(len(args)))
				self.cmdRunning = False
				continue
			
			callback(self.pom, args)
			
			self.cmdRunning = False

	def cmdMatch(self, cmd):
		cmds = self.cmdMatchRecur(cmd, self.cmdTree)
		if len(cmds) == 0:
			self.print("Command not found")
		elif len(cmds) > 1:
			self.print("Abiguous command")
		else:
			return cmds[0]
		return None

	def cmdMatchRecur(self, words, curTree):
		if len(words) == 0:
			try:
				result = [ (curTree['_cmd'], words) ]
			except KeyError:
				result = []
			return result
		word = words[0]
		myCmds = []
		for key in curTree:
			if key.startswith(word):
				cmds = self.cmdMatchRecur(words[1:], curTree[key])
				if not cmds == None:
					myCmds.extend(cmds)
			elif key == '_cmd':
				return [ (curTree['_cmd'], words) ]

		return myCmds

	def registerCmds(self, cmds):
		# split all the cmd
		for cmd in cmds:
			split_cmd = cmd['cmd'].split()
			curTree = self.cmdTree
			for word in split_cmd:
				if not word in curTree:
					curTree[word] = {}
				curTree = curTree[word]

			if '_cmd' in curTree:
				raise("Command '" + cmd['cmd'] + "' is already registered")
			else:
				curTree['_cmd'] = cmd

			signature = cmd['cmd']
			if 'signature' in cmd:
				signature = cmd['signature']
			if self.cmdSignatureMaxLen < len(signature):
				self.cmdSignatureMaxLen = len(signature)
		
	def completeRecur(self, words, curTree, completeCmd = True):
		if len(words) == 0:
			for key in curTree:
				self.curMatch.append(key)
			return
		word = words[0]
		for key in curTree:
			if key == '_cmd' and 'complete' in curTree['_cmd'] and completeCmd:
				completeCallback = curTree['_cmd']['complete']
				self.curMatch.extend(completeCallback(self.pom, words))
			elif key.startswith(word):
				if len(words) == 1:
					if key != '_cmd':
						self.curMatch.append(key)
				else:
					self.completeRecur(words[1:], curTree[key])

	def complete(self, prefix, state):
		origline = readline.get_line_buffer()
		end = readline.get_endidx()
		origline = origline[:end]
		splitted_line = origline.split()
		if len(origline) > 0 and origline[-1] == ' ':
			splitted_line.append('')
		if state == 0:
			self.completeRecur(splitted_line, self.cmdTree)

		response = None
		try:
			response = self.curMatch[state]
		except IndexError:
			self.curMatch = []
		return response + " "

	def cmdHelp(self, pom, args):
		if len(args) > 0:
			cmds = self.cmdMatchRecur(args, self.cmdTree)
			cmd = cmds[0][0]
			signature = cmd['cmd']
			if 'signature' in cmd:
				signature = cmd['signature']

			self.print(signature + " : " + cmd['help'])
		else:
			self.cmdHelpRecur(self.cmdTree)

	def cmdHelpRecur(self, curTree):
		wordList = curTree.keys()
		for word in sorted(wordList):
			if word == '_cmd':
				cmd = curTree['_cmd']	
				signature = cmd['cmd']
				if 'signature' in cmd:
					signature = cmd['signature']
				self.print(signature + " " * (self.cmdSignatureMaxLen - len(signature)) + " : " + cmd['help'])
			else:
				self.cmdHelpRecur(curTree[word])
	
	def completeHelp(self, pom, words):
		self.curMatch = []
		self.completeRecur(words, self.cmdTree)
		return self.curMatch

	def setConnected(self, connected):
		self.connected = connected
		old_prompt = self.prompt
		if self.connected:
			self.prompt = "pom> "
		else:
			self.prompt = "pom [disconnected]> "

		old_len = len(old_prompt)
		new_len = len(self.prompt)
		if new_len < old_len:
			for i in range(old_len - new_len):
				sys.stdout.write("\b")
			for i in range(old_len - new_len):
				sys.stdout.write(" ")
		sys.stdout.write("\r" + self.prompt + readline.get_line_buffer())
		

	def print(self, line):
		if self.cmdRunning:
			print(line)
			return
		
		buf = readline.get_line_buffer()
		tot_len = len(buf) + len(self.prompt)
		line_len = len(line)

		# erase extra characters
		if tot_len > line_len:
			for i in range(line_len - tot_len):
				sys.stdout.write("\b")
			for i in range(line_len - tot_len):
				sys.stdout.write(" ")
		sys.stdout.write("\r" + line + "\n" + self.prompt + buf)





import readline
import shlex

class console:

	prompt = "pom> "
	curMatch = []

	cmdTree = {}

	def __init__(self, pom):
		self.pom = pom
		readline.parse_and_bind("tab: complete")
		readline.set_completer(self.complete)

	def cmdloop(self):
		while 1:
			line = input(self.prompt)
			split_line = shlex.split(line)
			if len(split_line) == 0:
				continue

			res = self.cmdMatch(shlex.split(line))
			if res == None:
				continue

			callback = res[0]['callback']
			args = res[1]

			numargs = 0
			if 'numargs' in res[0]:
				numargs = res[0]['numargs']

			if len(args) != numargs:
				print("Invalid number of arguments. Expected", res[0]['numargs'], ", got ", len(args))
				continue
			
			callback(self.pom, args)
				

	def cmdMatch(self, cmd):
		cmds = self.cmdMatchRecur(cmd, self.cmdTree)
		if len(cmds) == 0:
			print("Command not found")
		elif len(cmds) > 1:
			print("Abiguous command")
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
		
	def completeRecur(self, words, curTree):
		if len(words) == 0:
			for key in curTree:
				self.curMatch.append(key)
			return
		word = words[0]
		for key in curTree:
			if key == '_cmd' and 'complete' in curTree['_cmd']:
				completeCallback = curTree['_cmd']['complete']
				self.curMatch.extend(completeCallback(self.pom, words))
			elif key.startswith(word):
				if len(words) == 1:
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


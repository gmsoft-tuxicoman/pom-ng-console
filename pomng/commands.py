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

def cmdRegistryReload(pom, args):
	pom.registry.fetch();
	pom.console.print("Registry reloaded");

def cmdRegistryDump(pom, args):
	pom.console.print(pom.registry.getClasses())

def cmdConfigSave(pom, args):
	pom.registry.save(args[0])

def cmdConfigLoad(pom, args):
	pom.registry.load(args[0])

def cmdConfigDelete(pom, args):
	pom.registry.delete_config(args[0])

def completeConfigList(pom, words):
	if len(words) != 1:
		return []
	configs = pom.registry.getConfigs()
	return [ x['name'] for x in configs if x['name'].startswith(words[0]) ]

def cmdConfigShowAll(pom, args):
	proxy = pom.registry.getProxy()
	classes = pom.registry.getClasses()
	for cls in classes:
		pom.console.print(cls + ":")
		cmdConfigShowClass(pom, cls, 1)
		

def cmdConfigShowClass(pom, clsName, tabs=0):

	cls = pom.registry.getClass(clsName)

	if len(cls['instances']) == 0:
		pom.console.print("\t" * tabs + "<no instance>")
		return

	perfList = {}
	perfList['input'] = [ 'bytes_in', 'pkts_in', 'runtime']
	perfList['output'] = [ 'events', 'bytes_out', 'pkts_out', 'files_open', 'files_closed', 'bytes_written' ]
	perfList['proto'] = [ 'conn_cur', 'conn_tot', 'pkts', 'bytes' ]
	perfList['datastore'] = [ 'read_queries', 'write_queries' ]

	for instName in sorted(cls['instances']):
		if clsName in perfList:
			cmdConfigShowInstance(pom, clsName, instName, tabs, perfList[clsName])
		else:
			cmdConfigShowInstance(pom, clsName, instName, tabs, [])



def cmdConfigShowInstance(pom, clsName, instName, tabs, perfList):

	cls = pom.registry.getClass(clsName)
	inst = pom.registry.getInstance(cls, instName)
	
	info = ""
	if 'running' in inst['parameters']:
		info += "running: " + inst['parameters']['running']['value']
	if 'type' in inst['parameters']:
		if len(info) > 0:
			info += ", "
		info += "type: " + inst['parameters']['type']['value']
	if len(info) > 0:
		info = " " + info


	filteredPerfList = [ x for x in perfList if x in inst['performances'] ]

	perf_str = ""
	if len(perfList):
		perfs = pom.registry.getInstancePerf(clsName, instName, filteredPerfList)
		if perfs:
			for perf in filteredPerfList:
				if len(perf_str) > 0:
					perf_str += ", "
				else:
					perf_str = " | "
				perf_str += perf + ": " + perfToHuman(perfs[perf])

	pom.console.print("\t" * tabs + instName + ":" + info + perf_str)
	if len(inst['parameters']) == 0:
		pom.console.print("\t" * tabs + "\t<no parameter>")
		return

	for paramName in sorted(inst['parameters']):
		if paramName == "running" or paramName == "type" or paramName == "uid":
			continue
		param = inst['parameters'][paramName]
		pom.console.print("\t" * tabs + "\t" + paramName + " : '" + param['value'] + "' (" + param['type'] + ")")
		

def cmdCoreGetVersion(pom, args):
	proxy = pom.registry.getProxy()
	pom.console.print("Pom-ng version is " + proxy.core.getVersion())

def cmdClassParameterShow(pom, args):
	classes = pom.registry.getClasses()
	for cls in classes:
		if not classes[cls]['parameters']:
			continue
		pom.console.print(cls + ":")
		params = classes[cls]['parameters']
		for paramName in sorted(params):
			param = params[paramName]
			pom.console.print("\t" + paramName + " : " + param['value'] + "' (" + param['type'] + ")")

def cmdClassParameterSet(pom, args):
	clsName = args[0]
	paramName = args[1]
	paramValue = args[2]
	pom.registry.setClassParameter(clsName, paramName, paramValue)

def completeClassParameterSet(pom, words):
	wordCount = len(words)

	if wordCount == 0:
		return []
	
	classes = pom.registry.getClasses()
	if wordCount == 1:
		return [ x for x in classes if classes[x]['parameters'] and x.startswith(words[0]) ]

	cls = classes[words[0]]
	if wordCount == 2:
		return [ x for x in cls['parameters'] if 'default_value' in cls['parameters'][x] and x.startswith(words[1]) ]

	return []

def cmdInstanceAdd(pom, instClass, args):
	instName = args[1]
	instType = args[0]
	pom.registry.addInstance(instClass, instName, instType)

def completeInstanceAdd(pom, instClass, words):
	if len(words) != 1:
		return []
	cls = pom.registry.getClass(instClass)
	return [ x['name'] for x in cls['available_types'] if x['name'].startswith(words[0]) ]

def cmdInstanceStartStop(pom, instClass, action, args):
	instName = args[0]
	cls = pom.registry.getClass(instClass)
	inst = pom.registry.getInstance(cls, instName)
	if not inst:
		pom.console.print(instClass + " '" + instName + "' does not exists")
		return
	if not pom.registry.setInstanceParameter(instClass, instName, "running", action):
		return
	if inst['parameters']['running']['value'] == action:
		state = "started" if action == 'yes' else "stopped"
		pom.console.print(instClass + " '" + instName + "' is already " + state)
		return

def completeInstanceStartStop(pom, instClass, words):
	if len(words) != 1:
		return []
	cls = pom.registry.getClass(instClass)
	return [ x for x in cls['instances'] if 'running' in cls['instances'][x]['parameters'] and x.startswith(words[0]) ]

def cmdInstanceRemove(pom, instClass, args):
	instName = args[0]
	pom.registry.removeInstance(instClass, instName)

def completeInstanceList(pom, instClass, words):
	if len(words) != 1:
		return []
	cls = pom.registry.getClass(instClass)
	return [ x for x in cls['instances'] if x.startswith(words[0]) ]

def cmdInstanceParameterSet(pom, instClass, args):
	instName = args[0]
	paramName = args[1]
	paramValue = args[2]
	pom.registry.setInstanceParameter(instClass, instName, paramName, paramValue)

def completeInstanceParameterSet(pom, instClass, words):
	wordCount = len(words)

	if wordCount == 0:
		return []

	cls = pom.registry.getClass(instClass)
	if wordCount == 1:
		return [ x for x in cls['instances'] if x.startswith(words[0]) and len(cls['instances'][x]['parameters']) > 0 ]

	instName = words[0]
	if not instName in cls['instances']:
		return []
	inst = cls['instances'][instName]

	if wordCount == 2:
		return [ x for x in inst['parameters'] if 'default_value' in inst['parameters'][x] and x.startswith(words[1]) and x != "running" ]

	return []

def perfToHuman(perf):

	value = perf['value']
	unit = perf['unit']
	if perf['type'] == 'timeticks':
		csec = (value / 10000) % 100
		s = value / 1000000
		m = s / 60
		h = m / 60
		s = s % 60
		m = m % 60

		if h < 24 :
			return "%02u:%02u:%02u.%02u" % (h, m, s, csec)
		else:
			d = h / 24
			h = h % 24
			if d < 2.0:
				return "1 day %02u:%02u:%02u.%02u" % (h, m, s, csec)
			else:
				return "%u days %02u:%02u:%02u.%02u" % (d, h, m, s, csec)

	divisor = 1000.0;
	units = [ '', 'k', 'm', 'g', 't']

	if unit == 'bytes':
		#bytes are multiple of 1024
		divisor = 1024.0
		units = [ '', 'K', 'M', 'G', 'T']

	if value <= 99999.0:
		return str(value)

	for i in range(len(units) - 1):
		if value > 99999.0:
			value /= divisor
		else:
			return "%3.1f%s" % (value, units[i])

	return "%3.1f%s" % (value, units[len(units) -1])

def cmdInstancePerfGet(pom, instClass, args):
	instName = args[0]
	cls = pom.registry.getClass(instClass)
	inst = pom.registry.getInstance(cls, instName)
	if not inst:
		pom.console.print(instClass + " '" + instName + "' does not exists")
		return
	if len(inst['performances']) == 0:
		pom.console.print(instClass + " '" + instName + "' does not have any performance object")
		return
	perfs = []
	for perf in inst['performances']:
		perfs.append({ 'class': instClass, 'instance': instName, 'perf': perf})

	perfs = pom.registry.getPerfs(perfs)

	for perf in perfs:
		pom.console.print(perf + ": " + perfToHuman(perfs[perf]))

def cmdClassPerfGet(pom, args):
	clsName = args[0]
	cls = pom.registry.getClass(clsName)
	if not cls:
		pom.console.print("class '" + clsName + "' does not exists")
		return
	if len(cls['performances']) == 0:
		pom.console.print("class '" + clsName + "' does not have any performance object")
		return
	perfs = []
	for perf in cls['performances']:
		perfs.append({ 'class': clsName, 'perf': perf})

	perfs = pom.registry.getPerfs(perfs)

	for perf in perfs:
		pom.console.print(perf + ": " + perfToHuman(perfs[perf]))

def completeClassList(pom, words):
	if len(words) != 1:
		return []
	classes = pom.registry.getClasses()
	return [ x for x in classes if x.startswith(words[0]) ]

def cmdLogShow(pom, args):
	numLogs = 0
	try:
		numLogs = int(args[0])
	except:
		pom.console.print("You must enter a valid number")
		return

	if numLogs <= 0:
		pom.console.print("You must enter a number bigger than 0")
		return

	logs = pom.getLastLog(numLogs)
	for log in logs:
		pom.console.print(log['data'])

def cmdLogLevelSet(pom, args):

	newLevel = 0
	levels = pom.getLoggingLevels()

	if args[0] in levels:
		newLevel = levels.index(args[0]) + 1
	else:
		try:
			newLevel = int(args[0])
		except:
			pom.console.print("New level must be an integer of 1-4 or any of " + str(levels))
			return

	if newLevel < 0 or newLevel > 4:
		pom.console.print("Log level must be 1-4")
		return

	pom.setLoggingLevel(newLevel)
	pom.console.print("Logging level set to '" + levels[newLevel] + "'")

def completeLogLevelSet(pom, words):
	if len(words) != 1:
		return []

	levels = pom.getLoggingLevels()
	levels.extend([ '0', '1', '2', '3', '4'])
	return [ x for x in levels if x.startswith(words[0]) ]

def cmdLogLevelGet(pom, args):
	levels = pom.getLoggingLevels()
	level = pom.getLoggingLevel()
	pom.console.print("Logging level set to '" + levels[level] + "' (" + str(level) + ")")

def cmdHalt(pom, args):
	pom.halt()


cmds = [
		# Analyzers function
		{
			'cmd'		: "analyzer parameter set",
			'signature'	: "analyzer parameter set <analyzer_name> <param_name>",
			'help'		: "Change the value of a parameter",
			'callback'	: lambda pom, args : cmdInstanceParameterSet(pom, "analyzer", args),
			'complete'	: lambda pom, words : completeInstanceParameterSet(pom, "analyzer", words),
			'numargs'	: 3
		},

		{
			'cmd'		: "analyzer show",
			'help'		: "Show all configured analyzers",
			'callback'	: lambda pom, args : cmdConfigShowClass(pom, "analyzer"),
		},

		# Config functions
		{
			'cmd'		: "config show",
			'help'		: "Show the whole configuration",
			'callback'	: cmdConfigShowAll
		},

		{
			'cmd'		: "config save",
			'help'		: "Save the current configuration",
			'signature'	: "config save <name>",
			'callback'	: cmdConfigSave,
			'complete'	: completeConfigList,
			'numargs'	: 1
		},

		{
			'cmd'		: "config load",
			'help'		: "Load a stored configuration from the system datastore",
			'signature'	: "config load <name>",
			'callback'	: cmdConfigLoad,
			'complete'	: completeConfigList,
			'numargs'	: 1
		},
		
		{
			'cmd'		: "config delete",
			'help'		: "Remove a stored configuration from the system datastore",
			'signature'	: "config delete <name>",
			'callback'	: cmdConfigDelete,
			'complete'	: completeConfigList,
			'numargs'	: 1
		},

		# Core functions
		{
			'cmd'		: "core get version",
			'help'		: "Get pom-ng version",
			'callback'	: cmdCoreGetVersion
		},

		# Datastore functions
		{
			'cmd'		: "datastore add",
			'signature'	: "datastore add <type> <name>",
			'help'		: "Add an datastore",
			'callback'	: lambda pom, args : cmdInstanceAdd(pom, "datastore", args),
			'complete'	: lambda pom, words : completeInstanceAdd(pom, "datastore", words),
			'numargs'	: 2
		},

		{
			'cmd'		: "datastore performance get",
			'signature'	: "datastore performance get <name>",
			'help'		: "Display the performance objects of an datastore",
			'callback'	: lambda pom, args : cmdInstancePerfGet(pom, "datastore", args),
			'complete'	: lambda pom, words : completeInstanceList(pom, "datastore", words),
			'numargs'	: 1
		},

		{
			'cmd'		: "datastore parameter set",
			'signature'	: "datastore parameter set <datastore_name> <param_name>",
			'help'		: "Change the value of a parameter",
			'callback'	: lambda pom, args : cmdInstanceParameterSet(pom, "datastore", args),
			'complete'	: lambda pom, words : completeInstanceParameterSet(pom, "datastore", words),
			'numargs'	: 3
		},

		{
			'cmd'		: "datastore remove",
			'signature'	: "datastore remove <name>",
			'help'		: "Remove an datastore",
			'callback'	: lambda pom, args : cmdInstanceRemove(pom, "datastore", args),
			'complete'	: lambda pom, words : completeInstanceList(pom, "datastore", words),
			'numargs'	: 1
		},

		{
			'cmd'		: "datastore show",
			'help'		: "Show all configured datastores",
			'callback'	: lambda pom, args : cmdConfigShowClass(pom, "datastore"),
		},

		# Input functions
		{
			'cmd'		: "input add",
			'signature'	: "input add <type> <name>",
			'help'		: "Add an input",
			'callback'	: lambda pom, args : cmdInstanceAdd(pom, "input", args),
			'complete'	: lambda pom, words : completeInstanceAdd(pom, "input", words),
			'numargs'	: 2
		},

		{
			'cmd'		: "input performance get",
			'signature'	: "input performance get <name>",
			'help'		: "Display the performance objects of an input",
			'callback'	: lambda pom, args : cmdInstancePerfGet(pom, "input", args),
			'complete'	: lambda pom, words : completeInstanceList(pom, "input", words),
			'numargs'	: 1
		},

		{
			'cmd'		: "input parameter set",
			'signature'	: "input parameter set <input_name> <param_name>",
			'help'		: "Change the value of a parameter",
			'callback'	: lambda pom, args : cmdInstanceParameterSet(pom, "input", args),
			'complete'	: lambda pom, words : completeInstanceParameterSet(pom, "input", words),
			'numargs'	: 3
		},

		{
			'cmd'		: "input remove",
			'signature'	: "input remove <name>",
			'help'		: "Remove an input",
			'callback'	: lambda pom, args : cmdInstanceRemove(pom, "input", args),
			'complete'	: lambda pom, words : completeInstanceList(pom, "input", words),
			'numargs'	: 1
		},

		{
			'cmd'		: "input show",
			'help'		: "Show all configured inputs",
			'callback'	: lambda pom, args : cmdConfigShowClass(pom, "input"),
		},

		{
			'cmd'		: "input start",
			'signature'	: "input start <name>",
			'help'		: "Start an input",
			'callback'	: lambda pom, args : cmdInstanceStartStop(pom, "input", "yes", args),
			'complete'	: lambda pom, words : completeInstanceStartStop(pom, "input", words),
			'numargs'	: 1
		},

		{
			'cmd'		: "input stop",
			'signature'	: "input stop <name>",
			'help'		: "Start an input",
			'callback'	: lambda pom, args : cmdInstanceStartStop(pom, "input", "no", args),
			'complete'	: lambda pom, words : completeInstanceStartStop(pom, "input", words),
			'numargs'	: 1
		},

		# Global functions
		{
			'cmd'		: "global parameter set",
			'signature'	: "global parameter set <class> <param_name> <param_value>",
			'help'		: "Change a global parameter",
			'callback'	: cmdClassParameterSet,
			'complete'	: completeClassParameterSet,
			'numargs'	: 3
		},

		{
			'cmd'		: "global parameter show",
			'help'		: "Display all the global parameters",
			'callback'	: cmdClassParameterShow
		},

		{
			'cmd'		: "global performance get",
			'signature'	: "global performance get <class>",
			'help'		: "Display the performance objects of a class",
			'callback'	: cmdClassPerfGet,
			'complete'	: completeClassList,
			'numargs'	: 1
		},

		# Output functions
		{
			'cmd'		: "output add",
			'signature'	: "output add <type> <name>",
			'help'		: "Add an output",
			'callback'	: lambda pom, args : cmdInstanceAdd(pom, "output", args),
			'complete'	: lambda pom, words : completeInstanceAdd(pom, "output", words),
			'numargs'	: 2
		},

		{
			'cmd'		: "output performance get",
			'signature'	: "output performance get <name>",
			'help'		: "Display the performance objects of an output",
			'callback'	: lambda pom, args : cmdInstancePerfGet(pom, "output", args),
			'complete'	: lambda pom, words : completeInstanceList(pom, "output", words),
			'numargs'	: 1
		},

		{
			'cmd'		: "output parameter set",
			'signature'	: "output parameter set <output_name> <param_name>",
			'help'		: "Change the value of a parameter",
			'callback'	: lambda pom, args : cmdInstanceParameterSet(pom, "output", args),
			'complete'	: lambda pom, words : completeInstanceParameterSet(pom, "output", words),
			'numargs'	: 3
		},

		{
			'cmd'		: "output remove",
			'signature'	: "output remove <name>",
			'help'		: "Remove an output",
			'callback'	: lambda pom, args : cmdInstanceRemove(pom, "output", args),
			'complete'	: lambda pom, words : completeInstanceList(pom, "output", words),
			'numargs'	: 1
		},

		{
			'cmd'		: "output show",
			'help'		: "Show all configured outputs",
			'callback'	: lambda pom, args : cmdConfigShowClass(pom, "output"),
		},

		{
			'cmd'		: "output start",
			'signature'	: "output start <name>",
			'help'		: "Start an output",
			'callback'	: lambda pom, args : cmdInstanceStartStop(pom, "output", "yes", args),
			'complete'	: lambda pom, words : completeInstanceStartStop(pom, "output", words),
			'numargs'	: 1
		},

		{
			'cmd'		: "output stop",
			'signature'	: "output stop <name>",
			'help'		: "Start an output",
			'callback'	: lambda pom, args : cmdInstanceStartStop(pom, "output", "no", args),
			'complete'	: lambda pom, words : completeInstanceStartStop(pom, "output", words),
			'numargs'	: 1
		},

		# Protocol functions
		{
			'cmd'		: "proto parameter set",
			'signature'	: "proto parameter set <proto_name> <param_name>",
			'help'		: "Change the value of a parameter",
			'callback'	: lambda pom, args : cmdInstanceParameterSet(pom, "proto", args),
			'complete'	: lambda pom, words : completeInstanceParameterSet(pom, "proto", words),
			'numargs'	: 3
		},

		{
			'cmd'		: "proto performance get",
			'signature'	: "proto performance get <name>",
			'help'		: "Display the performance objects of an proto",
			'callback'	: lambda pom, args : cmdInstancePerfGet(pom, "proto", args),
			'complete'	: lambda pom, words : completeInstanceList(pom, "proto", words),
			'numargs'	: 1
		},

		{
			'cmd'		: "proto show",
			'help'		: "Show all configured protos",
			'callback'	: lambda pom, args : cmdConfigShowClass(pom, "proto"),
		},


		# Registry functions
		{
			'cmd'		: "registry dump",
			'help'		: "Dump the whole registry",
			'callback'	: cmdRegistryDump
		},

		{
			'cmd'		: "registry reload",
			'help'		: "Reload the registry if it gets out of sync",
			'callback'	: cmdRegistryReload
		},

		# Logs functions
		{
			'cmd'		: "log level set",
			'help'		: "Set the logging level to be displayed",
			'callback'	: cmdLogLevelSet,
			'complete'	: completeLogLevelSet,
			'numargs'	: 1
		},

		{
			'cmd'		: "log level get",
			'help'		: "Display the current loging level that will be displayed",
			'callback'	: cmdLogLevelGet
		},

		{
			'cmd'		: "log show",
			'help'		: "Show the last logs",
			'callback'	: cmdLogShow,
			'numargs'	: 1
		},

		# Other functions
		{
			'cmd'		: "halt",
			'help'		: "Shutdown pom-ng",
			'callback'	: cmdHalt,
		}
		
	]

def commandsRegister(console):
	console.registerCmds(cmds)

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

	for instName in cls['instances']:
		cmdConfigShowInstance(pom, cls, instName, tabs)


def cmdConfigShowInstance(pom, clsName, instName, tabs=0):
	inst = pom.registry.getInstance(clsName, instName)
	
	info = ""
	if 'running' in inst['parameters']:
		info += "running: " + inst['parameters']['running']['value']
	if 'type' in inst['parameters']:
		if len(info) > 0:
			info += ", "
		info += "type: " + inst['parameters']['type']['value']

	if len(info) > 0:
		info = " (" + info + ")"

	pom.console.print("\t" * tabs + instName + ":" + info)
	if len(inst['parameters']) == 0:
		pom.console.print("\t" * tabs + "\t<no parameter>")
		return

	for paramName in inst['parameters']:
		if paramName == "running" or paramName == "type" or paramName == "uid":
			continue
		param = inst['parameters'][paramName]
		pom.console.print("\t" * tabs + "\t" + paramName + " : '" + param['value'] + "' (" + param['type'] + ")")
		

def cmdCoreGetVersion(pom, args):
	proxy = pom.registry.getProxy()
	pom.console.print("Pom-ng version is " + proxy.core.getVersion())

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
	if inst['parameters']['running']['value'] == action:
		state = "started" if action == 'yes' else "stopped"
		pom.console.print(instClass + " '" + instName + "' is already " + state)
		return
	pom.registry.setInstanceParameter(instClass, instName, "running", action)

def completeInstanceStartStop(pom, instClass, words):
	if len(words) != 1:
		return []
	cls = pom.registry.getClass(instClass)
	return [ x for x in cls['instances'] if 'running' in cls['instances'][x]['parameters'] and x.startswith(words[0]) ]

def cmdInstanceRemove(pom, instClass, args):
	instName = args[0]
	pom.registry.removeInstance(instClass, instName)

def completeInstanceRemove(pom, instClass, words):
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

	if newLevel < 1 or newLevel > 4:
		pom.console.print("Log level must be 1-4")

	pom.setLoggingLevel(newLevel)
	pom.console.print("Logging level set to '" + levels[newLevel - 1] + "'")

def completeLogLevelSet(pom, words):
	if len(words) != 1:
		return []

	levels = pom.getLoggingLevels()
	levels.extend([ '1', '2', '3', '4'])
	return [ x for x in levels if x.startswith(words[0]) ]

def cmdLogLevelGet(pom, args):
	levels = pom.getLoggingLevels()
	level = pom.getLoggingLevel()
	pom.console.print("Logging level set to '" + levels[level - 1] + "' (" + str(level) + ")")

def cmdHalt(pom, args):
	pom.halt()


cmds = [

		# Config functions
		{
			'cmd'		: "config show",
			'help'		: "Show the whole configuration",
			'callback'	: cmdConfigShowAll
		},

		{
			'cmd'		: "config save",
			'signature'	: "config save <name>",
			'callback'	: cmdConfigSave,
			'numargs'	: 1
		},

		{
			'cmd'		: "config load",
			'signature'	: "config load <name>",
			'callback'	: cmdConfigLoad,
			'complete'	: completeConfigList,
			'numargs'	: 1
		},
		
		{
			'cmd'		: "config delete",
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
			'complete'	: lambda pom, words : completeInstanceRemove(pom, "datastore", words),
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
			'complete'	: lambda pom, words : completeInstanceRemove(pom, "input", words),
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
			'complete'	: lambda pom, words : completeInstanceRemove(pom, "output", words),
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

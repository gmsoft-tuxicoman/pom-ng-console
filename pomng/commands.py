
def cmdRegistryReload(registry, args):
	registry.load();
	print("Registry reloaded");

def cmdRegistryDump(registry, args):
	print(registry.getClasses())

def cmdConfigShow(registry, args):
	proxy = registry.getProxy()
	classes = registry.getClasses()
	for cls in classes:
		print(cls, ":")

		for inst in classes[cls]['instances']:
			print("\t", inst)
		

def cmdCoreGetVersion(registry, args):
	proxy = registry.getProxy()
	print("Pom-ng version is " + proxy.core.getVersion())

def cmdInstanceAdd(registry, instClass, args):
	instName = args[1]
	instType = args[0]
	registry.addInstance(instClass, instName, instType)

def completeInstanceAdd(registry, instClass, words):
	if len(words) != 1:
		return []
	cls = registry.getClass(instClass)
	return [ x['name'] for x in cls['available_types'] if x['name'].startswith(words[0]) ]

def cmdInstanceRemove(registry, instClass, args):
	instName = args[0]
	registry.removeInstance(instClass, instName)

def completeInstanceRemove(registry, instClass, words):
	if len(words) != 1:
		return []
	cls = registry.getClass(instClass)
	return [ x for x in cls['instances'] if x.startswith(words[0]) ]

cmds = [

		# Config functions
		{
			'cmd'		: "config show",
			'help'		: "Show the whole configuration",
			'callback'	: cmdConfigShow
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
			'callback'	: lambda registry, args : cmdInstanceAdd(registry, "datastore", args),
			'complete'	: lambda registry, words : completeInstanceAdd(registry, "datastore", words),
			'numargs'	: 2
		},

		{
			'cmd'		: "datastore remove",
			'signature'	: "datastore remove <name>",
			'help'		: "Remove an datastore",
			'callback'	: lambda registry, args : cmdInstanceRemove(registry, "datastore", args),
			'complete'	: lambda registry, words : completeInstanceRemove(registry, "datastore", words),
			'numargs'	: 1
		},

		# Input functions
		{
			'cmd'		: "input add",
			'signature'	: "input add <type> <name>",
			'help'		: "Add an input",
			'callback'	: lambda registry, args : cmdInstanceAdd(registry, "input", args),
			'complete'	: lambda registry, words : completeInstanceAdd(registry, "input", words),
			'numargs'	: 2
		},

		{
			'cmd'		: "input remove",
			'signature'	: "input remove <name>",
			'help'		: "Remove an input",
			'callback'	: lambda registry, args : cmdInstanceRemove(registry, "input", args),
			'complete'	: lambda registry, words : completeInstanceRemove(registry, "input", words),
			'numargs'	: 1
		},

		# Output functions
		{
			'cmd'		: "output add",
			'signature'	: "output add <type> <name>",
			'help'		: "Add an output",
			'callback'	: lambda registry, args : cmdInstanceAdd(registry, "output", args),
			'complete'	: lambda registry, words : completeInstanceAdd(registry, "output", words),
			'numargs'	: 2
		},

		{
			'cmd'		: "output remove",
			'signature'	: "output remove <name>",
			'help'		: "Remove an output",
			'callback'	: lambda registry, args : cmdInstanceRemove(registry, "output", args),
			'complete'	: lambda registry, words : completeInstanceRemove(registry, "output", words),
			'numargs'	: 1
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
		}
		
	]

def commandsRegister(console):
	console.registerCmds(cmds)


def cmdRegistryReload(registry, args):
	registry.load();
	print("Registry reloaded");

def cmdRegistryDump(registry, args):
	print(registry.getClasses())

def cmdConfigShow(registry, args):
	proxy = registry.getProxy()
	classes = registry.getClasses()
	for cls in classes:
		print(cls['name'], ":")

		for inst in cls['instances']:
			print("\t", inst['name'])
		

def cmdCoreGetVersion(registry, args):
	proxy = registry.getProxy()
	print("Pom-ng version is " + proxy.core.getVersion())

def cmdInputAdd(registry, args):
	inputName = args[0]
	inputType = args[1]
	registry.addInstance("input", inputName, inputType)

cmds = [
		{
			'cmd'		: "config show",
			'help'		: "Show the whole configuration",
			'callback'	: cmdConfigShow
		},

		{
			'cmd'		: "core get version",
			'help'		: "Get pom-ng version",
			'callback'	: cmdCoreGetVersion
		},

		{
			'cmd'		: "input add",
			'help'		: "Add an input",
			'callback'	: cmdInputAdd,
			'numargs'	: 2
		},

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

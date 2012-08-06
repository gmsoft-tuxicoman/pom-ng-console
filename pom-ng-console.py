#!/usr/bin/python3
import pomng
import xmlrpc.client

proxy = None
prompt = "pom> "

# First connect to an pom-ng instance
while proxy == None:
	host = input("Enter pom-ng host (localhost) : ")
	if host == "":
		host = "localhost"
	url = "http://" + host + ":8080/RPC2"
	print("Connecting to " + url + " ...")

	version = ""

	try:
		proxy = xmlrpc.client.ServerProxy(url)
		print("Connected to pom-ng version " + proxy.core.getVersion())
	except Exception as e:
		print("Could not connect to " + url + " :", e)
		proxy = None


registry = pomng.registry(proxy)
console = pomng.console(registry)

# Now process the commands

pomng.commandsRegister(console)

console.cmdloop()

	

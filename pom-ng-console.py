#!/usr/bin/python3
import pomng
import xmlrpc.client

pom = None
prompt = "pom> "

# First connect to an pom-ng instance
while pom == None:
	host = input("Enter pom-ng host (localhost) : ")
	if host == "":
		host = "localhost"
	url = "http://" + host + ":8080/RPC2"
	try:
		pom = pomng.pom(url)
		print("Connected to pom-ng version " + pom.getVersion())
	except Exception as e:
		print("Could not connect to " + url + " :", e)
		pom = None

console = pomng.console(pom)

# Now process the commands

pomng.commandsRegister(console)

console.cmdloop()

	

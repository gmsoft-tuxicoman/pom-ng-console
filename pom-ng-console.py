#!/usr/bin/python3
#  This file is part of pom-ng-console.
#  Copyright (C) 2012-2013 Guy Martin <gmsoft@tuxicoman.be>
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

import pomng
import xmlrpc.client
import sys

pom = None

def pom_connect(url):

	if (not url.startswith("http")):
		url = "http://" + url + ":8080/RPC2"
	
	if (not url.endswith("RPC2")):
		if (url.endswith("/")):
			url += "RPC2"
		else:
			url += "/RPC2"

	try:
		pom = pomng.pom(url)
		print("Connected to pom-ng version " + pom.getVersion())
		return pom
	except Exception as e:
		print("Could not connect to " + url + " :", e)
		return None

if len(sys.argv) > 1:
	pom = pom_connect(sys.argv[1])
	if pom == None:
		sys.exit()
else:
	while pom == None:
		try:
			host = input("Enter pom-ng host or url (localhost) : ")
		except:
			print("\n")
			sys.exit()
		if host == "":
			host = "localhost"
		pom = pom_connect(host)

console = pomng.console(pom)

# Now process the commands

pomng.commandsRegister(console)

console.cmdloop()


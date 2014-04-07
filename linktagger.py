#!/usr/bin/python3
# ^ Update this with the path to Python 3 on your machine

import fileinput, re, sys, os, os.path, glob, fnmatch

# Set initial variables
filestotag = []
taggedfiles = []
backupmode = "" # none
recursion = False
removeglt = False
tagging = False
# path = "."
# Compile the regular expressions
idbeforeend = re.compile(r'<a([^>]*)href="([^"\#]*)(\#[^"]*)(\?[^"]*)"')
hasglt = re.compile(r'(\?|\&|\&amp;)utm_[^?#"]*')
no_id = re.compile(r'<a([^>]*)href="([^"]*http[^#?"]*?)"')
hasid = re.compile(r'<a([^>]*)href="([^"]*http[^#?"]*?)#([^\"]*?)"')
parametersno_id = re.compile(r'<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?![^#"]*?utm_)[^#"]*?)"')
parametershasid = re.compile(r'<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?!.*?utm_).*?)(#*[^#"]*)"')
notargetblank = re.compile(r'<a([^>]*)href="([^"]*http[^"]*?[^"]*)">')

# Begin functions

# Interpret parameters
def interpretparameter(mode):
	global recursion
	global backupmode
	global removeglt
	if mode == "-rf":
		recursion = True
	if mode == "-backup":
		backupmode = ".backup"
	if mode == "-strip":
		removeglt = True

# Remove parameters
def checkparameters(filestotag):
	newfiles = []
	for file in filestotag:
		if file[0] == "-":
			interpretparameter(file) # Interpret arguments preceded by a hyphen
		else:
			newfiles.append(file)
	return newfiles

# Expand wildcards through subdirectories
def expandrecursively(filestotag):
	recursivematches = []
	for file in filestotag:
		if file.find(os.path.sep) != -1:
			splitversion = file.rsplit(os.path.sep, 1)
			file = splitversion[1]
			path = splitversion[0]
		else:
			path = "."
		for root, dirnames, filenames in os.walk(path):
			filenames = [f for f in filenames if not f[0] == '.']
			dirnames[:] = [d for d in dirnames if not d[0] == '.']
			for filename in fnmatch.filter(filenames, file):
				recursivematches.append(os.path.join(root, filename))
	return recursivematches

# Expand wildcards in current working directory
def expandwildcards(filestotag):
	wildcardmatches = []
	for file in filestotag:
		for expandedfile in glob.glob(file):
			wildcardmatches.append(expandedfile) # Shoot expanded files into the list
	return wildcardmatches

def removeextras(filestotag):
	newfiles = []
	for file in filestotag:
		if file.endswith(".backup") is False:
			if os.path.abspath(file) != os.path.abspath(__file__):
				newfiles.append(file)
	return newfiles

def checkencoding(filestotag):
	newfiles = []
	for file in filestotag:
			with open(file, "r+") as f:
				try:
					for line in f:
						pass
					newfiles.append(file)
				except:
					print("Skipping", file, " because we can't read and write to it")
					continue
	return newfiles

def printfinalfiles(filestotag):
	newfiles = []
	for file in filestotag:
		try:
			print(file) # Docs that include weird characters in the name--but not the body--can still trigger an exception; remove them, too.
			newfiles.append(file)
		except:
			pass
	return newfiles

# Begin user interaction:
for word in sys.argv:
	word = word.replace("\"\"", "") # Remove quotation marks, which we only needed to prevent the shell from expanding wildcards
	filestotag.append(word)
filestotag = checkparameters(filestotag) # Remove and interpret arguments preceded by "-"
if recursion == True:
	filestotag = expandrecursively(filestotag)
else:
	filestotag = expandwildcards(filestotag)
filestotag = checkencoding(filestotag) # Keep only the files we can read and write to
filestotag = removeextras(filestotag) # Remove .backups and the script itself
if len(filestotag) is 0:
	print("\nNo files to tag!")
else:
	print("\nFiles to tag:")
	filestotag = printfinalfiles(filestotag) # Perform final check and print all files to tag
	type=input("\nType e to paste in existing GLT, or n to build new GLT: ")
	if type == "e" or type == "E":
		tagging = True
		glt = input("Right-click and paste in GLT: ")
		if glt[0] == "?" or glt[0] == "&": # If there's a leading question mark or ampersand, trim it
			glt = glt[1:]
	elif type == "n" or type == "N":
		tagging = True
		source = input("Enter source: ")
		medium = input("Enter medium: ")
		content = input("Enter content: ")
		campaign = input("Enter campaign: ")
		glt = "utm_source=" + source + "&utm_medium=" + medium + "&utm_content=" + content + "&utm_campaign=" + campaign
		glt = glt.lower()
	addtargetblank = input("Add target=\"_blank\"? y/n: ")
	for file in filestotag:
		changes = False
		print("Scanning", file, "...")
		for line in fileinput.input(file, inplace=1, backup=backupmode):
			try:
			    m = re.search(idbeforeend, line)
			    if m:
			    	changes = True
			    line = re.sub(idbeforeend,'<a\\1href="\\2\\4\\3"', line.rstrip()) # Put section IDs at the end
			    if removeglt == True:
			    	m = re.search(hasglt, line)
			    	if m:
			    		changes = True
				    	line = re.sub(hasglt,'', line.rstrip()) # Strip GLT
			    if tagging == True:
			    	m = re.search(no_id, line)
			    	if m:
			    		changes = True
			    		line = re.sub(no_id,'<a\\1href="\\2?' + glt + '"', line.rstrip()) # Tag links without any section ID
		    		m = re.search(hasid, line)
		    		if m:
		    			changes = True
		    			line = re.sub(hasid,'<a\\1href="\\2?' + glt + '#\\3"', line.rstrip()) # Tag links with section ID, before the ID
	    			m = re.search(parametersno_id, line)
	    			if m:
	    				changes = True
	    				line = re.sub(parametersno_id,'<a\\1href="\\2\\3&' + glt + '"', line.rstrip()) # Tag links with other parameters (but no GLT) and no section ID
	    			m = re.search(parametershasid, line)
	    			if m:
	    				changes = True
	    				line = re.sub(parametershasid,'<a\\1href="\\2\\3&' + glt + '\\4"', line.rstrip())
			    if addtargetblank == "y" or addtargetblank == "Y":
			    	m = re.search(notargetblank, line)
			    	if m:
			    		changes = True
			    		line = re.sub(notargetblank,'<a\\1href="\\2" target="_blank">', line.rstrip()) # Append target="_blank"
			    print(line) # Prints to file
			except:
				print("aha!")
				continue
		if changes == True:
			taggedfiles.append(file)
	scannedcount = len(filestotag)
	taggedcount = len(taggedfiles)
	if scannedcount == 1:
		scannedref = "file"
	else:
		scannedref = "files"
	if taggedcount == 1:
		taggedref = "file"
	else:
		taggedref = "files"
	for file in taggedfiles:
		print("Tagged:", file)
	print("Done!", scannedcount, scannedref, "scanned;", taggedcount, taggedref, "changed.")
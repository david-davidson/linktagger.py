#!/usr/bin/python3
# ^ Update this with your computer's path

import fileinput, re, sys, os, os.path, glob, fnmatch, codecs

#Set initial variables
filestotag = []
backupmode = "" # none
recursion = False
removeglt = False
tagging = False
path = "."

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

def checkparameters(filestotag):
	newfiles = []
	for file in filestotag:
		if file[0] == "-":
			interpretparameter(file) # Interpret arguments preceded by a hyphen
		else:
			newfiles.append(file) # Remove them; they're not files
	return newfiles

def expandrecursively(filestotag):
	recursivematches = []
	global path
	for file in filestotag:
		if file.find(os.path.sep) != -1:
			splitversion = file.rsplit(os.path.sep, 1)
			file = splitversion[1]
			path = splitversion[0]
		for root, dirnames, filenames in os.walk(path):
			filenames = [f for f in filenames if not f[0] == '.']
			dirnames[:] = [d for d in dirnames if not d[0] == '.']
			for filename in fnmatch.filter(filenames, file):
				recursivematches.append(os.path.join(root, filename))
	return recursivematches

def expandwildcards(filestotag):
	wildcardmatches = []
	for file in filestotag:
		for expandedfile in glob.glob(file):
			# sexpandedfile = "." + os.path.sep + expandedfile
			wildcardmatches.append(expandedfile) # Shoot expanded files into the list
	return wildcardmatches

def checkencoding(filestotag):
	newfiles = []
	for currentfile in filestotag:
		clean = True
		try:
			f = codecs.open(currentfile, encoding="windows-1252", errors="strict")
			try:
				for line in f:
					pass
				try:
					f = codecs.open(currentfile, encoding="utf-8", errors="strict")
					try:
						for line in f:
							pass
					except:
						clean = False
						print("Skipping", currentfile, "because it's unreadable in utf-8")
				except:
					clean = False
					pass
			except:
				clean = False
				print("Skipping", currentfile, "because it's unreadable in windows-1252")		
		except:
			clean = False
			pass
		if clean == True:
			newfiles.append(currentfile)
	return newfiles

def sanitize(filestotag):
	newfiles = []
	for file in filestotag:
		if os.access(file, os.W_OK) is True:
			if os.access(file, os.R_OK) is True:
				if file.endswith(".backup") is False:
					if os.path.abspath(file) != os.path.abspath(__file__):
						newfiles.append(file)
			else:
				print("Skipping", file, ": can't read from it")
		else:
			print("Skipping", file, ": can't write to it")
	return newfiles

def printfinalfiles(filestotag):
	newfiles = []
	for file in filestotag:
		try:
			print(file) # Somehow certain docs can sneak through the UTF-8 and windows-1252 filters and still throw an exception in print(). We remove them, too.
			newfiles.append(file)
		except:
			pass
	return newfiles

# BEGIN USER INTERACTION
for word in sys.argv:
	word = word.replace("\"\"", "") # Remove quotation marks, which we only needed to prevent the shell from expanding wildcards
	if word != __file__: # Don't try to tag the script itself :)
		filestotag.append(word) # Create initial list of arguments
filestotag = checkparameters(filestotag) # Remove and interpret arguments preceded by "-"
if recursion == True:
	filestotag = expandrecursively(filestotag)
else:
	filestotag = expandwildcards(filestotag)
filestotag = sanitize(filestotag)
filestotag = checkencoding(filestotag)
if len(filestotag) is 0:
	print("\nNo files to tag!")
else:
	print("\nFiles to tag:")
	filestotag = printfinalfiles(filestotag) # Performs final check and prints all files to tag
	type=input("\nType e to paste in existing GLT, or n to build new GLT: ")
	if type == "e" or type == "E":
		tagging = True
		glt = input("Right-click and paste in GLT: ")
		if glt[0] == "?" or glt[0] == "&": # If there's a leading question mark, trim it
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
		print("Scanning", file, "...")
		for line in fileinput.input(file, inplace=1, backup=backupmode):
		    line = re.sub('<a([^>]*)href="([^"\#]*)(\#[^"]*)(\?[^"]*)"','<a\\1href="\\2\\4\\3"', line.rstrip()) # Put section IDs at the end
		    if removeglt == True:
		    	line = re.sub('(\?|\&|\&amp;)utm_[^?#"]*','', line.rstrip()) # Strip GLT
		    if tagging == True:
			    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)"','<a\\1href="\\2?' + glt + '"', line.rstrip()) # Tag links without any section ID
			    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)#([^\"]*?)"','<a\\1href="\\2?' + glt + '#\\3"', line.rstrip()) # Tag links with section ID, before the ID
			    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?![^#"]*?utm_)[^#"]*?)"','<a\\1href="\\2\\3&' + glt + '"', line.rstrip()) # Tag links with other parameters (but no GLT) and no section ID
			    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?!.*?utm_).*?)(#*[^#"]*)"','<a\\1href="\\2\\3&' + glt + '\\4"', line.rstrip()) # Tag links with other parameters (but no GLT) and a section ID at the end
		    if addtargetblank == "y" or addtargetblank == "Y":
			    line = re.sub('<a([^>]*)href="([^"]*http[^"]*?[^"]*)">','<a\\1href="\\2" target="_blank">', line.rstrip()) # Append target="_blank"
		    print(line) # Prints to file
	filecount = len(filestotag)
	if filecount == 1:
		filereference = "file"
	else:
		filereference = "files"
	print("Done!", filecount, filereference, "scanned")
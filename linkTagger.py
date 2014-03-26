#!/usr/bin/python3
# ^ Note "python3", not "python", because Cygwin currently installs both. You may not need to do this--run "python -V"; if your version is 3+, you can just set the location to /python

import fileinput, re, sys, os, os.path, glob, fnmatch, codecs

#Set initial variables
filestotag = []
backupmode = "" # none
recursion = False
removeglt = False
tagging = False
path = "."
me = "linktagger.py"

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
	for file in filestotag:
		if file[0] == "-":
			interpretparameter(file) # Interpret arguments preceded by a hyphen
			filestotag.remove(file) # Remove them; they're not files
			checkparameters(filestotag) # Start from the top, since we can't just iterate over the rest of the list. (All the remaining files have shifted one to the left, so we would skip one.)

def split(file, character):
	global path
	splitversion = file.rsplit(character, 1)
	file = splitversion[1]
	path = splitversion[0] + character
	return file

def expandrecursively(filestotag):
	recursivematches = []
	global path
	for file in filestotag:
		if file.find("/") != -1: # First, check if "/" in path
			file = split(file, "/")
		elif file.find("\\") != -1:
			file = split(file, "\\") # Then if "\" in path
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
			wildcardmatches.append(expandedfile) # Shoot expanded files into the list
	return wildcardmatches

def checkencoding(filestotag):
	newfiles = []
	for file in filestotag:
		try:
			f = codecs.open(file, encoding="utf-8", errors="strict")
			for line in f:
				pass
			f.close
			try:
				f = codecs.open(file, encoding="windows-1252", errors="strict")
				for line in f:
					pass
				f.close
				newfiles.append(file)
			except UnicodeDecodeError:
				print("Skipping " + file + " because it's not Win-1252")
		except UnicodeDecodeError:
			print("Skipping " + file + " because it's not UTF-8")
	return newfiles

def sanitize(filestotag):
	newfiles = []
	for file in filestotag:
		if os.access(file, os.W_OK) is True:
			if os.access(file, os.R_OK) is True:
				if file.endswith(".backup") is False:
					if file.find(__file__) == -1:
						newfiles.append(file)
			else:
				print("Skipping ", file, ": can't read from it")
		else:
			print("Skipping ", file, ": can't write to it")
	return newfiles

# Begin user interaction
for word in sys.argv:
	word = word.replace("\"\"", "") # Remove quotation marks, which we only needed to prevent the shell from expanding wildcards
	if word != __file__: # Don't try to tag the script itself :)
		filestotag.append(word) # Create initial list of arguments
checkparameters(filestotag) # Remove and interpret arguments preceded by "-"
if recursion == True:
	filestotag = expandrecursively(filestotag)
else:
	filestotag = expandwildcards(filestotag)
filestotag = sanitize(filestotag)
filestotag = checkencoding(filestotag)
if len(filestotag) is 0:
	print("No files to tag!")
else:
	type=input("Type e to paste in existing GLT, or n to build new GLT: ")
	if type == "e" or type == "E":
		tagging = True
		glt = input("Right-click and paste in GLT: ")
		if glt[0] == "?": # If there's a leading question mark, trim it
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
	print("Scanning files: hold on a sec!")
	for line in fileinput.input(filestotag, inplace=1, backup=backupmode):
	    line = re.sub('<a([^>]*)href="([^"\#]*)(\#[^"]*)(\?[^"]*)"','<a\\1href="\\2\\4\\3"', line.rstrip()) # Put section IDs at the end
	    if removeglt == True:
	    	line = re.sub('[\?|\&]utm_[^?#"]*','', line.rstrip())
	    if tagging == True:
		    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)"','<a\\1href="\\2?' + glt + '"', line.rstrip()) # Tag links without any section ID
		    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)#([^\"]*?)"','<a\\1href="\\2?' + glt + '#\\3"', line.rstrip()) # Tag links with section ID, before the ID
		    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?![^#"]*?utm_)[^#"]*?)"','<a\\1href="\\2\\3&' + glt + '"', line.rstrip()) # Tag links with other parameters (but no GLT) and no section ID
		    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?!.*?utm_).*?)(#*[^#"]*)"','<a\\1href="\\2\\3&' + glt + '\\4"', line.rstrip()) # Tag links with other parameters (but no GLT) and a section ID at the end
	    else:
    		line = line.rstrip() # If we don't use the rstrip(), we'll add a ton of new lines!
	    if addtargetblank == "y" or addtargetblank == "Y":
		    line = re.sub('<a([^>]*)href="([^"]*http[^"]*?[^"]*)">','<a\\1href="\\2" target="_blank">', line.rstrip()) # Append target="_blank"
	    print(line) # Writes directly to the file
	for file in filestotag:
		print("Scanned: ", file)
	print("Done!")
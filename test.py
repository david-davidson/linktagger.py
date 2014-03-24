#!/usr/bin/python3
# ^ Note "python3", not "python", because Cygwin currently installs both. You may not need to do this--run "python -V"; if your version is 3+, you can just set the location to /python

import fileinput, re, sys, os, os.path, glob, fnmatch

#Set initial variables
filestotag = []
recursivematches = []
backupmode = "" # none
recursion = False
removeglt = False


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
		if file[0] == "-": # Interpret parameters preceded by a hyphen, and...
			interpretparameter(file)
			filestotag.remove(file) # <= N2S: Add recursive global function
			checkparameters(filestotag)

# Begin script
for word in sys.argv:
	word = word.replace("\"\"", "") # We ask for quotation marks only to prevent the shell from expanding wildcards; we can remove them right
	if word != __file__: # Don't try to tag the script itself :)
		filestotag.append(word) # Create initial list of arguments
checkparameters(filestotag)
if recursion == True:
	for file in filestotag:
		if file.find("/") != -1:
			head = file.rsplit("/", 1)
			file = head[1]
			head = head[0]
			path = head + "/"
		elif file.find("\\") != -1:
			head = file.rsplit("\\", 1)
			file = head[1]
			head = head[0]
			path = head + "\\"
		else:
			path = "."
		for root, dirnames, filenames in os.walk(path):
			for filename in fnmatch.filter(filenames, file):
				recursivematches.append(os.path.join(root, filename))
	filestotag = recursivematches
for file in filestotag:
	if file.find("*") != -1: # Expand wilcards, but only in current working directory
		filestotag.remove(file)
		for expandedfile in glob.glob(file):
			filestotag.append(expandedfile) # Shoot expanded files into the list
for file in filestotag:
	if os.path.isfile(file) is not True:
		print("LOL WUT \""+ file + "\" is not a file")
		filestotag.remove(file)
	if file.endswith(".backup"):
		filestotag.remove(file)
if len(filestotag) is 0:
	print("No files to tag!")
else:
	# source = input("Enter source: ")
	# medium = input("Enter medium: ")
	# content = input("Enter content: ")
	# campaign = input("Enter campaign: ")
	# glt = "utm_source=" + source + "&utm_medium=" + medium + "&utm_content=" + content + "&utm_campaign=" + campaign
	# print(glt) # For now
	glt = "temp" # Remove
	for file in filestotag:
		print(file)
	for line in fileinput.input(filestotag, inplace=1, backup=backupmode):
	    line = re.sub('<a([^>]*)href="([^"\#]*)(\#[^"]*)(\?[^"]*)"','<a\\1href="\\2\\4\\3"', line.rstrip()) # Put section IDs at the end
	    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)"','<a\\1href="\\2?' + glt + '"', line.rstrip()) # Tag links without any section ID
	    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)#([^\"]*?)"','<a\\1href="\\2?' + glt + '#\\3"', line.rstrip()) # Tag links with section ID, before the ID
	    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?![^#"]*?utm_)[^#"]*?)"','<a\\1href="\\2\\3&' + glt + '"', line.rstrip()) # Tag links with other parameters (but no GLT) and no section ID
	    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?!.*?utm_).*?)(#*[^#"]*)"','<a\\1href="\\2\\3&' + glt + '\\4"', line.rstrip()) # Tag links with other parameters (but no GLT) and a section ID at the end
	    line = re.sub('<a([^>]*)href="([^"]*http[^"]*?[^"]*)">','<a\\1href="\\2" target="_blank">', line.rstrip()) # Append target="_blank"
	    print(line) # Writes directly to the file
	print("Done!")
# print("Testing")
# allfiles =[]
# for root, dirs, files in os.walk("."):
# 	for name in files:
# 		allfiles.append(name)
# print(allfiles)
# Use scenarios for recursive tagging:
# tag -rf index.html (every index.html in every directory)
# tag -rf *.* (every file in every directory)
# recursivefiles = [os.path.join(root, name)
#     for root, dirs, files in os.walk(".")
#         for name in files
#             if name.endswith((".html"))]
# for name in recursivefiles:
# 	print(name)
#print(os.path.basename(__file__))
#person = input('Enter your name: ')
#print('Hello', person)
# type = sys.argv[1]
# backupMode = ".backup"
# allfilesintree = [os.path.join(root, name)
#     for root, dirs, filestotag in os.walk(".")
#         for name in filestotag
#             if name.endswith(("." + type))]
# #print allfilestotag
# for name in allfilestotag:
# 	print name


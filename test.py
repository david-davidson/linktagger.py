#!/usr/bin/python3
# ^ Note "python3", not "python", because Cygwin installs both. You may not need to do this--run "python -V"; if your version is 3+, you can just set the location to /python
# Ideal command-line syntax? "glt *.txt -backup -rf"
import fileinput
import re
import sys
import sys
import os
import os.path
import glob

#Set initial variables
backupmode = ""
filestotag = []
glt = "utm_source=test&utm_medium=test&utm_content=test&utm_campaign=test"

# Interpret command-line parameters
def getparameters(mode):
	global backupmode
	if mode == "-rf":
		print("Mode: recursive!")
	if mode == "-backup":
		backupmode = ".backup"

# Parse command-line input
# We no longer need this
def process(word):
	global filestotag
	word = word.replace("\"\"", "")
	if word != None and word[0] == "-": # Handle parameters preceded by a hyphen
		getparameters(word)
		word = None
	if word != None and word.find("*") != -1:
		for file in glob.glob(word):
			process(file) # Expand wildcards, and shoot individual files right back into process()
		word = None
	if word != None and word == __file__: # Remove the script name itself
		word = None
	if word != None:
		filestotag.append(word)
	return word

# Begin script
for word in sys.argv:
	word = word.replace("\"\"", "")
	if word != __file__: # Don't include the script's own name
		filestotag.append(word)
for file in filestotag:
	if file[0] == "-": # Remove, interpret parameters preceded by a hyphen
		filestotag.remove(file)
		getparameters(file)
for file in filestotag:
	if file.find("*") != -1: # Expand wilcards
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
	person = input('Enter your name: ')
	print('Hello', person)
	source = input('Enter source: ')
	print(source)
	medium = input('Enter medium: ')
	content = input('Enter content: ')
	campaign = input('Enter campaign: ')
	glt = 'utm_source=' + source + '&utm_medium=' + medium + '&utm_content=' + content + '&utm_campaign=' + campaign
	print(glt)
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
#print(os.path.basename(__file__))
#person = input('Enter your name: ')
#print('Hello', person)
# type = sys.argv[1]
# backupMode = ".backup"
# allfilestotag = [os.path.join(root, name)
#     for root, dirs, filestotag in os.walk(".")
#         for name in filestotag
#             if name.endswith(("." + type))]
# #print allfilestotag
# for name in allfilestotag:
# 	print name


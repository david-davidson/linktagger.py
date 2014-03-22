#!/usr/bin/python
# Ideal command-line syntax? "glt *.txt -backup -rf"
import fileinput
import re
import sys
import sys
import os
backupmode = ""
def getparameters(mode):
	global backupmode
	if mode == "-rf":
		print("Mode: recursive!")
	if mode == "-backup":
		backupmode = ".backup"
files = []
glt = "utm_source=test&utm_medium=test&utm_content=test&utm_campaign=test"
# Parse command-line input:
for word in sys.argv:
	if word[0] == "-": # Handle parameters preceded by a hyphen
		getparameters(word)
		word = None
	if word == __file__: # Remove the script name itself
		word = None
	if word is not None:
		files.append(word)
#print(files)
for line in fileinput.input(files, inplace=1, backup=backupmode): # Only problem: if you do *.html, it treats the second HTML file as sys.argv[2]--that is, as the mode, not a file!
    line = re.sub('<a([^>]*)href="([^"\#]*)(\#[^"]*)(\?[^"]*)"','<a\\1href="\\2\\4\\3"', line.rstrip()) # Put section IDs at the end
    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)"','<a\\1href="\\2?' + glt + '"', line.rstrip()) # <= Tag links without any section ID
    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)#([^\"]*?)"','<a\\1href="\\2?' + glt + '#\\3"', line.rstrip()) # <= Tag links with section ID, before the ID
    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?![^#"]*?utm_)[^#"]*?)"','<a\\1href="\\2\\3&' + glt + '"', line.rstrip()) # <= Tag links with other parameters (but no GLT) and no section ID
    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?!.*?utm_).*?)(#*[^#"]*)"','<a\\1href="\\2\\3&' + glt + '\\4"', line.rstrip()) # <= Tag links with other parameters (but no GLT) and a section ID at the end
    line = re.sub('<a([^>]*)href="([^"]*http[^"]*?[^"]*)">','<a\\1href="\\2" target="_blank">', line.rstrip()) # Append target="_blank"
    print(line)
print("Done!")
#print(os.path.basename(__file__))
#person = input('Enter your name: ')
#print('Hello', person)
# type = sys.argv[1]
# backupMode = ".backup"
# allfiles = [os.path.join(root, name)
#     for root, dirs, files in os.walk(".")
#         for name in files
#             if name.endswith(("." + type))]
# #print allfiles
# for name in allfiles:
# 	print name


#!/usr/bin/python
import fileinput
import re
import sys
glt = "?TESTGLT"
import sys
script = sys.argv[0]
file = sys.argv[1]
try:
	mode = sys.argv[2]
except IndexError:
	mode = "nonrecursive"
print "Script: " + script
print "File: " + file
print "Mode: " + mode
for line in fileinput.input(file, inplace=1, backup='.backup'): # Only problem: if you do *.html, it treats the second HTML file as sys.argv[2]--that is, as the mode, not a file!
    line = re.sub('<a([^>]*)href="([^"\#]*)(\#[^"]*)(\?[^"]*)"','<a\\1href="\\2\\4\\3"', line.rstrip())
    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)"','<a\\1href="\\2' + glt + '"', line.rstrip()) # <= Works, but ONLY on links w/ section ID
    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)#([^\"]*?)"','<a\\1href="\\2' + glt + '#\\3"', line.rstrip()) # <= Works, but ONLY on links w/ section ID
    print(line)
print "Done!"
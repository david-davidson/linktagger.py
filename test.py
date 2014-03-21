#!/usr/bin/python
# Ideal command-line syntax? "glt *.txt -backup -rf"
import fileinput
import re
import sys
glt = "utm_source=test&utm_medium=test&utm_content=test&utm_campaign=test"
import sys
script = sys.argv[0]
file = sys.argv[1]
try:
	backupMode = sys.argv[2]
except IndexError:
	backupMode = ""
print("Script: " + script)
print("File: " + file)
print("Backup Mode: " + backupMode)
if (backupMode == "-backup"):
	backupMode = ".backup"
for line in fileinput.input(file, inplace=1, backup=backupMode): # Only problem: if you do *.html, it treats the second HTML file as sys.argv[2]--that is, as the mode, not a file!
    line = re.sub('<a([^>]*)href="([^"\#]*)(\#[^"]*)(\?[^"]*)"','<a\\1href="\\2\\4\\3"', line.rstrip()) # Put section IDs at the end
    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)"','<a\\1href="\\2?' + glt + '"', line.rstrip()) # <= Tag links without any section ID
    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)#([^\"]*?)"','<a\\1href="\\2' + glt + '#\\3"', line.rstrip()) # <= Tag links with section ID, before the ID
    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?!.*?utm_).*?)(#*[^#"]*)"','<a\\1href="\\2\\3&' + glt + '\\4"', line.rstrip()) # <= Still not working with parameters but no ID!
    line = re.sub('<a([^>]*)href="([^"]*http[^"]*?[^"]*)">','<a\\1href="\\2" target="_blank">', line.rstrip()) # Append target="_blank"
    print(line)
print("Done!")


# Could be useful? http://stackoverflow.com/questions/18210968/python-search-through-directory-trees-rename-certain-files
# Or this? http://stackoverflow.com/questions/1597649/replace-strings-in-files-by-python
# Again with os.walk(path): http://stackoverflow.com/questions/5817209/browse-files-and-subfolders-in-python
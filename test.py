#!/usr/bin/python
import fileinput
import re
glt = "?TESTGLT"
for line in fileinput.input(inplace=1, backup='.backup'):
    line = re.sub('<a([^>]*)href="([^"\#]*)(\#[^"]*)(\?[^"]*)"','<a\\1href="\\2\\4\\3"', line.rstrip())
    line = re.sub('<a([^>]*)href="([^"]*http[^#?"]*?)#([^\"]*?)"','<a\\1href="\\2' + glt + '#\\3"', line.rstrip()) # <= Works, but ONLY on links w/ section ID
    print(line)

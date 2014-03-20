#!/usr/bin/python
import fileinput
import re
glt = "TESTGLT"
for line in fileinput.input(inplace=1, backup='.backup'):
    line = re.sub('<a([^>]*)href="([^"\#]*)(\#[^"]*)(\?[^"]*)"','<a\\1href="\\2\\4\\3"' + glt, line.rstrip())
    line = re.sub('<a([^>]*)href="([^"]*http[^"?\#]*)(\#[^"]*)"','<a\\1href="\\2' + glt + '\\3"' + glt, line.rstrip()) # <= Super messed up
    # line = re.sub('', '<a\\1href="\\2\\3', line.rstrip())
    # s/<a(.*?)href="([^"]*http[^#?"]*?)(#[^\"]*?)*"/<a$1href="$2\?$glt$3"/g;
    print(line)

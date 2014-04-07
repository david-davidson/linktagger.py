#!/usr/bin/python3
# ^ Update this with the path to Python 3 on your machine

import fileinput, re, sys, os, os.path, glob, fnmatch

# Set initial variables
files_to_tag = []
tagged_files = []
backup_mode = "" # Default behavior: no backups
recursion = False
remove_glt = False
tagging = False
backup_suffix = ".backup" # <= Feel free to change this

# Compile the regular expressions
id_before_end = re.compile(r'<a([^>]*)href="([^"\#]*)(\#[^"]*)(\?[^"]*)"')
has_glt = re.compile(r'(\?|\&|\&amp;)utm_[^?#"]*')
has_no_id = re.compile(r'<a([^>]*)href="([^"]*http[^#?"]*?)"')
has_id = re.compile(r'<a([^>]*)href="([^"]*http[^#?"]*?)#([^\"]*?)"')
has_parameters_has_no_id = re.compile(r'<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?![^#"]*?utm_)[^#"]*?)"')
has_parameters_has_id = re.compile(r'<a([^>]*)href="([^"]*http[^#?"]*?)(\?(?!.*?utm_).*?)(#*[^#"]*)"')
no_target_blank = re.compile(r'<a([^>]*)href="([^"]*http[^"]*?[^"]*)">')

#================
# Begin functions
#================

# Interpret parameters
def interpret_parameters(mode):
	global recursion
	global backup_mode
	global remove_glt
	if mode == "-rf":
		recursion = True
	if mode == "-backup":
		backup_mode = backup_suffix
	if mode == "-strip":
		remove_glt = True

# Remove parameters
def check_parameters(files_to_tag):
	new_files = []
	for file in files_to_tag:
		if file[0] == "-":
			interpret_parameters(file) # Interpret arguments preceded by a hyphen
		else:
			new_files.append(file) # And treat other arguments as files to be tagged
	return new_files

# Expand wildcards through subdirectories
def expand_recursively(files_to_tag):
	recursive_matches = []
	for file in files_to_tag:
		if file.find(os.path.sep) != -1: # If the path separator is present, split on the rightmost occurrence
			split = file.rsplit(os.path.sep, 1)
			path = split[0] # Set path aside for later
			file = split[1] # Trim file to version without path
		else:
			path = "."
		for root, dirnames, filenames in os.walk(path):
			filenames = [f for f in filenames if not f[0] == '.'] # Omit secret files
			dirnames[:] = [d for d in dirnames if not d[0] == '.'] # Omit secret directories
			for filename in fnmatch.filter(filenames, file):
				recursive_matches.append(os.path.join(root, filename))
	return recursive_matches

# Expand wildcards in current working directory
def expand_wildcards(files_to_tag):
	wildcard_matches = []
	for file in files_to_tag:
		for expandedfile in glob.glob(file):
			wildcard_matches.append(expandedfile)
	return wildcard_matches

def sanitize(files_to_tag):
	new_files = []
	for file in files_to_tag:
		if os.path.isfile(file):
			try:
				with open(file, "r+") as f: # Can we open it?
					try:
						for line in f: # Can we read through it?
							pass
						if file.endswith(backup_suffix) is False: # Is it a backup?
							if os.path.abspath(file) != os.path.abspath(__file__): # Is the the script itself?
								new_files.append(file) # No? Well then, it's sanitized!
					except:
						print("Skipping", file, " because we can't read and write to it")
						continue
			except:
				print("Skipping", file, " because we can't access it right now")
				continue
	return new_files

def print_final_files(files_to_tag):
	new_files = []
	for file in files_to_tag:
		try:
			print(file) # Docs that include weird characters in the name--but not the body--can still trigger an exception; remove them, too.
			new_files.append(file)
		except:
			pass
	return new_files


# Begin user interaction:
for word in sys.argv:
	word = word.replace("\"\"", "") # Remove quotation marks, which we only needed to prevent the shell from expanding wildcards
	files_to_tag.append(word)
files_to_tag = check_parameters(files_to_tag) # Remove and interpret arguments preceded by "-"
if recursion == True:
	files_to_tag = expand_recursively(files_to_tag)
else:
	files_to_tag = expand_wildcards(files_to_tag)
files_to_tag = sanitize(files_to_tag) # Narrow the files down to just those we should tag
if len(files_to_tag) is 0:
	print("\nNo files to tag!")
else:
	print("\nMatching files:")
	files_to_tag = print_final_files(files_to_tag) # Perform final check and print all files to tag
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
	add_target_blank = input("Add target=\"_blank\"? y/n: ")
	for file in files_to_tag:
		changes = False
		print("Scanning", file, "...")
		for line in fileinput.input(file, inplace=1, backup=backup_mode):
			try:
			    m = re.search(id_before_end, line)
			    if m:
			    	changes = True
			    line = re.sub(id_before_end,'<a\\1href="\\2\\4\\3"', line.rstrip()) # Put section IDs at the end
			    if remove_glt == True:
			    	m = re.search(has_glt, line)
			    	if m:
			    		changes = True
				    	line = re.sub(has_glt,'', line.rstrip()) # Strip GLT
			    if tagging == True:
			    	m = re.search(has_no_id, line)
			    	if m:
			    		changes = True
			    		line = re.sub(has_no_id,'<a\\1href="\\2?' + glt + '"', line.rstrip()) # Tag links without any section ID
		    		m = re.search(has_id, line)
		    		if m:
		    			changes = True
		    			line = re.sub(has_id,'<a\\1href="\\2?' + glt + '#\\3"', line.rstrip()) # Tag links with section ID, before the ID
	    			m = re.search(has_parameters_has_no_id, line)
	    			if m:
	    				changes = True
	    				line = re.sub(has_parameters_has_no_id,'<a\\1href="\\2\\3&' + glt + '"', line.rstrip()) # Tag links with other parameters (but no GLT) and no section ID
	    			m = re.search(has_parameters_has_id, line)
	    			if m:
	    				changes = True
	    				line = re.sub(has_parameters_has_id,'<a\\1href="\\2\\3&' + glt + '\\4"', line.rstrip())
			    if add_target_blank == "y" or add_target_blank == "Y":
			    	m = re.search(no_target_blank, line)
			    	if m:
			    		changes = True
			    		line = re.sub(no_target_blank,'<a\\1href="\\2" target="_blank">', line.rstrip()) # Append target="_blank"
			    print(line) # Prints to file
			except:
				continue
		if changes == True:
			tagged_files.append(file)
	scanned_count = len(files_to_tag)
	tagged_count = len(tagged_files)
	if scanned_count == 1:
		scanned_ref = "file"
	else:
		scanned_ref = "files"
	if tagged_count == 1:
		tagged_ref = "file"
	else:
		tagged_ref = "files"
	for file in tagged_files:
		print("Tagged:", file)
	print("Done!", scanned_count, scanned_ref, "scanned;", tagged_count, tagged_ref, "changed.")
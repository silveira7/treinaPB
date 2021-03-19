#!/usr/bin/env python3

"""This module removes non-words from the .lab files"""

import os
import sys
import re

# Current working directory must have a list of .lab files
os.chdir(sys.argv[1])

# Store a list with the name of the files of current folder
files_list = os.listdir(os.getcwd())

# List for .lab files
lab_files = list()

# Store in lab_files only files with .lab
for file in list(files_list):
    if re.search(r'\.lab', file):
        lab_files.append(file)

# For each .lab file, open it, clean it and overwrite the original version
for file in lab_files:
    with open(file, 'r') as opened_file:
        lines = opened_file.readline()
    if re.search(r'{.*}|xxx|\(xxx\)|"|\(|\)|/|\?|\.|,|-|<.*>', lines):
        changed_lines = re.sub(
            r'{.*}|\(xxx\)|xxx|"|^ *| *$|\(*|\)*|/*|\\*|\?*|\.*|,*|!*|<.*>', r'',
            lines)
        changed_lines = re.sub(r' {2}', r' ', changed_lines)
        changed_lines = re.sub(r'-', r' ', changed_lines)
        changed_lines = re.sub(r'\bcd\b', r'cedê', changed_lines)
        changed_lines = re.sub(r'c\b', r'que', changed_lines)
        with open(file, 'w') as opened_file:
            opened_file.write(changed_lines)

# If the transcription file is empty, delete it and its matching audio
for file in lab_files:
    if os.stat(file)[6] == 0:
        if os.path.exists(file):
            os.remove(file)
            print(f"{file} deleted.")
        else:
            print(f"{file} not found.")
        if os.path.exists(file[:-4] + ".wav"):
            os.remove(file[:-4] + ".wav")
            print(f"{file[:-4]}.wav deleted.")
        else:
            print(f"{file[:-4]} not found.")

print("Concluded!")

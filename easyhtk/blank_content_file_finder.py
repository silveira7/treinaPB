"""Script that searches for .lab files filled with only blank chars"""

import os
import re

PATH = "/home/gustavo/Documentos/Amostras_de_fala/SP2010/media_files/"

files = sorted(os.listdir(PATH))
labs = list()

for file in files:
    if ".lab" in file:
        labs.append(file)

matches = list()

for file in labs:
    with open(PATH + file) as opened_file:
        lines = opened_file.readlines()
    for line in lines:
        if re.search(r'^\s+$', line):
            matches.append(file)

if matches:
    for match in matches:
        print(match)
else:
    print("No matches found.")

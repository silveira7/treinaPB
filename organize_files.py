#!/usr/bin/env python3

"""This module moves the files of each speaker to a separated folder"""

import os
import re
import sys

folder = sys.argv[1]

os.chdir(folder)

files = sorted(os.listdir(folder))

speakers = list()
for file in files:
    if re.search(r'\.', file):
        print(file)
        speakers.append(file.split(sep='_')[2])

speakers = set(speakers)
print(speakers)

try:
    os.makedirs('final')
except FileExistsError:
    pass

for speaker in speakers:
    try:
        os.makedirs(f'final/{speaker}')
    except FileExistsError:
        pass

for speaker in speakers:
    for file in files:
        if re.search(speaker, file) and re.search('merged', file):
            os.rename(file, f'final/{speaker}/{file}')

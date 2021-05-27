import sys
from pathlib import Path
import re

input_dict = sys.argv[1]

p = Path(input_dict)

with open(p) as open_file:
    lines = open_file.readlines()

ehI = re.compile(r'\beh I\b')
ohI = re.compile(r'\boh I\b')
sil = re.compile(r'\bsil\b')
dZ = re.compile(r'\bdZ\b')
tS = re.compile(r'\btS\b')

for index, line in enumerate(lines):
    if ehI.search(line):
        lines[index] = ehI.sub(r'eI', line)
for index, line in enumerate(lines):
    if ohI.search(line):
        lines[index] = ohI.sub(r'oI', line)
for index, line in enumerate(lines):
    if sil.search(line):
        lines[index] = sil.sub(r's i l', line)
for index, line in enumerate(lines):
    if dZ.search(line):
        lines[index] = dZ.sub(r'd', line)
for index, line in enumerate(lines):
    if tS.search(line):
        lines[index] = tS.sub(r't', line)

for index, line in enumerate(list(lines)):
    if line == "\n":
        lines.remove(line)

fixed = ''.join(lines)

with open(p, 'w') as open_file:
    open_file.write(fixed)

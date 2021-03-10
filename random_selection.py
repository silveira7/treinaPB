#!/usr/bin/env python3

"""This modules moves a random selection of media/transcription pairs to a
separated folder"""

import os
import re
import sys
import random

path = sys.argv[1]
n_choices = int(sys.argv[2])

folders = os.listdir(path)

for folder in folders:
    old_folder = os.path.join(path, folder)
    new_folder = os.path.join(path, folder, 'selection')

    try:
        os.mkdir(new_folder)
    except FileExistsError:
        pass

    files = os.listdir(old_folder)

    uniques = list()

    for file in files:
        if re.search('wav', file):
            uniques.append(file[0:-4])

    selection = random.sample(uniques, k=n_choices)

    tg = {}
    wav = {}
    
    for file in selection:
        scr = os.path.join(old_folder, file + '.TextGrid')
        dst = os.path.join(new_folder, file + '.TextGrid')
        tg[scr] = dst

        scr = os.path.join(old_folder, file + '.wav')
        dst = os.path.join(new_folder, file + '.wav')
        wav[scr] = dst

    for src, dst in tg.items():
        os.rename(src, dst)

    for src, dst in wav.items():
        os.rename(src, dst)

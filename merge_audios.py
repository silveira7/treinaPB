#!/usr/bin/env python3

"""This module merges the audios of the same group of annotations"""

import os
import re
import sys
from pydub import AudioSegment

folder = sys.argv[1]

os.chdir(folder)

files = sorted(os.listdir(folder))
wav_files = list()

for file in files:
    if re.search('.wav', file):
        wav_files.append(file)

metadata = dict()

for file in wav_files:
    speaker = file.split(sep='_')[0:3]
    speaker = '_'.join(speaker)
    group = file.split(sep='_')[3]
    metadata.setdefault(speaker, dict())
    metadata[speaker].setdefault(group, [file])
    if file not in metadata[speaker][group]:
        metadata[speaker][group].append(file)

for speaker in metadata.keys():
    for group in metadata[speaker].keys():
        audio = None
        for file in metadata[speaker][group]:
            if audio is None:
                audio = AudioSegment.from_wav(file)
            else:
                audio += AudioSegment.from_wav(file)
        audio.export(f'{speaker}_{group}_merged.wav', format='wav')

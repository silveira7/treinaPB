#!/usr/bin/env python3

""" This script merge the .wav files of each group"""

from pathlib import Path
from pydub import AudioSegment


def retrieve(input_dir):
    p = Path(input_dir)
    waves = sorted(list(p.glob('*.wav')))
    group_done = []

    for wav in waves:
        if 'Isolated' not in wav.name:
            file_info = wav.name.split(sep='_')[0:3]
            group_id = '_'.join(file_info)
            if group_id not in group_done:
                print(f'Merging waves of speaker {file_info[1]}',
                      f'and group {file_info[2]}')
                group_done.append(group_id)
                group_waves = sorted(list(p.glob(f'*{group_id}*.wav')))
                for index, each_wav in enumerate(group_waves):
                    if index == 0:
                        merged_waves = AudioSegment.from_wav(each_wav)
                    else:
                        merged_waves += AudioSegment.from_wav(each_wav)
                filepath = p / f'{group_id}_merged.wav'
                merged_waves.export(filepath, format="wav")

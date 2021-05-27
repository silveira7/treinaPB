#!/usr/bin/env python3

"""This modules moves a random selection of media/transcription pairs to a
separated folder"""

from pathlib import Path
import random


p = Path('/home/gustavo/Documentos/Corpora/ALCP/Chunks/')
n_choices = int(10)

for speaker_folder in p.iterdir():
    selection_path = speaker_folder / 'Selection'
    selection_path.mkdir(exist_ok=True)

    uniques = []

    for speaker_file in speaker_folder.glob('*.wav'):
        uniques.append(Path(speaker_file))

    selection = random.sample(uniques, k=n_choices)

    suffixes = ['.TextGrid', '.wav']

    for file in selection:
        if 'Isolated' in file.stem:
            for suffix in suffixes:
                file.with_suffix(suffix).rename(
                    selection_path / file.with_suffix(suffix).name)
        else:
            for suffix in suffixes[0:2]:
                file.with_suffix(suffix).rename(
                    selection_path / file.with_suffix(suffix).name)

"""This module moves the files of each speaker to a separated folder"""

from pathlib import Path


def organize(folder):
    p = Path(folder)

    p_intervals = p / 'intervals'
    p_final = p / 'final'

    p_intervals.mkdir(exist_ok=True)
    p_final.mkdir(exist_ok=True)

    for path in p.iterdir():
        if path.is_file():
            if path.match('*merged.TextGrid'):
                speaker = path.stem.split(sep='_')[2]
                p_speaker = p_final / f'{speaker}'
                p_speaker.mkdir(exist_ok=True)
                path.rename(p_speaker / path.name)
            else:
                path.rename(p_intervals / path.name)

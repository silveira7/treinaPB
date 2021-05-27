#!/usr/bin/env python3

from pathlib import Path


def final_clean(input_dir):
    p = Path(input_dir)
    for file in p.iterdir():
        if 'merged' not in file.name and 'Isolated' not in file.name:
            file.unlink()

        if 'Isolated' in file.name:
            new_name = '_'.join(file.name.split(sep='_')[0:4]) + file.suffix
            file.rename(file.parent / new_name)

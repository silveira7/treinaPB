#!/usr/bin/env python3

from pathlib import Path
import wave
import contextlib


def delete_small_isolated(input_dir):
    waves = list(Path(input_dir).glob('*Isolated*.wav'))
    for wav in waves:
        with contextlib.closing(wave.open(str(wav), 'r')) as open_wav:
            frames = open_wav.getnframes()
            rate = open_wav.getframerate()
            duration = frames / float(rate)
            if duration < 4:
                lab = wav.parent / wav.with_suffix(".lab")
                wav.unlink()
                lab.unlink()

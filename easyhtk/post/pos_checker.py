#!/usr/bin/env python3

"""This script checks the integrity of all merged .wav files"""

# TODO Checar se todos os áudios tem mais de 4 segundos

from pathlib import Path
import wave
import contextlib


def check(input_dir):
    p = Path(input_dir)
    waves = list(p.glob("*merged.wav"))
    broken_audios = []
    short_audios = []
    less_four = 0
    right = 0
    large_six = 0

    for wav in waves:
        if wav.stat().st_size < 1000:
            broken_audios.append(wav.name)

        with contextlib.closing(wave.open(str(wav), 'r')) as open_wav:
            frames = open_wav.getnframes()
            rate = open_wav.getframerate()
            duration = frames / float(rate)
        if duration > 6:
            large_six += 1
        elif duration < 4:
            less_four += 1
        else:
            right += 1

    print(less_four, right, large_six)

    if broken_audios:
        print("Bad news! The following audios are corrupted:")
        for audio in broken_audios:
            print("\n\t", audio)
    else:
        print("Nice! There is no broken audio.")

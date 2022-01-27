from pathlib import Path
import sys
import string
import re
import enchant
import json
import wave
import contextlib

br = enchant.Dict('pt_BR')


def _get_labs(input_dir):
    """Get the list of .lab files"""
    labs = list(Path(input_dir).glob('*.lab'))
    return labs


def _get_waves(input_dir):
    """Get the list of .wav files"""
    waves = list(Path(input_dir).glob('*.wav'))
    return waves


def multiline(input_dir):
    """Turn multi-lines .labs into one-line file"""
    print("Fixing LAB files with more than one line...")
    labs = _get_labs(input_dir)

    for lab in labs:
        with open(lab, 'r') as open_file:
            lines = open_file.readlines()

        # Check if there is more than one line
        if len(lines) > 1:
            mod_lines = ''.join(lines)
            mod_lines = re.sub(r'\n', '', mod_lines)
            with open(lab, 'w') as open_file:
                open_file.write(mod_lines)


def punctwhite(input_dir):
    """Remove punctuations and extra spaces"""
    print("Removing punctations and extra spaces...")
    labs = _get_labs(input_dir)

    for lab in labs:
        with open(lab, 'r') as open_file:
            lines = open_file.readlines()

        # Remove punctations
        cleaned_string = lines[0].translate(
            str.maketrans('', '', string.punctuation))

        # Remove marginal whitespaces
        cleaned_string = cleaned_string.strip()

        cleaned_string = cleaned_string.lower()

        # Remove duplicate whitespaces
        cleaned_string = re.sub(' +', ' ', cleaned_string)

        # Write cleaned file
        with open(lab, 'w') as opened_file:
            opened_file.write(cleaned_string)


def nonwords(input_dir, output_dir):
    """Remove groups with non-words in Portuguese"""
    print("Checking if all words are Brazilian words...")
    labs = _get_labs(input_dir)
    to_remove = []
    non_words = {}

    for lab in labs:
        with open(lab, 'r') as open_file:
            line = open_file.readline()

        word_list = line.split(sep=' ')

        for word in word_list:
            if not br.check(word.strip()):
                non_words[lab.name] = word

                if 'Isolated' in lab.name:
                    group_id = '_'.join(lab.name.split(sep='_')[0:4])
                else:
                    group_id = '_'.join(lab.name.split(sep='_')[0:3])

                group_files = list(Path(input_dir).glob(f'{group_id}*'))

                for file in group_files:
                    to_remove.append(file)

                break

    for file in to_remove:
        file.unlink(missing_ok=True)

    print(f"{len(to_remove)} files removed due to non-words.")

    non_words_json = json.dumps(non_words, indent=4)
    new_files_path = Path(output_dir)

    with open(new_files_path / "nonwords.json", 'w') as opened_file:
        opened_file.write(non_words_json)


def isoletter(input_dir):
    """Remove isolated consonants"""
    print("Removing isolated consonant letters...")
    labs = _get_labs(input_dir)
    to_remove = []

    for lab in labs:
        with open(lab) as open_file:
            line = open_file.readline()

        letter = re.compile(r'\b[bcdfghijklmnpqrstuvwxyz]\b')

        if letter.search(line):
            if 'Isolated' in lab.name:
                group_id = '_'.join(lab.name.split(sep='_')[0:4])
            else:
                group_id = '_'.join(lab.name.split(sep='_')[0:3])

            group_files = list(Path(input_dir).glob(f'{group_id}*'))

            for file in group_files:
                to_remove.append(file)

    for file in to_remove:
        file.unlink(missing_ok=True)


def empties(input_dir):
    """Delete groups with empty labs"""
    print("Deleting empty LAB files...")
    labs = _get_labs(input_dir)
    to_remove = []

    for lab in labs:
        if lab.stat().st_size == 0:

            if 'Isolated' in lab.name:
                group_id = '_'.join(lab.name.split(sep='_')[0:4])
            else:
                group_id = '_'.join(lab.name.split(sep='_')[0:3])

            group_files = list(Path(input_dir).glob(f'{group_id}*'))

            for file in group_files:
                to_remove.append(file)

    for file in to_remove:
        file.unlink(missing_ok=True)


def broken_audios(input_dir):
    """Delete groups with broken audios"""
    print("Deleting broken WAV files...")
    waves = _get_waves(input_dir)
    to_remove = []

    for wav in waves:
        if wav.stat().st_size < 1000:
            if 'Isolated' in wav.name:
                group_id = '_'.join(wav.name.split(sep='_')[0:4])
            else:
                group_id = '_'.join(wav.name.split(sep='_')[0:3])

            group_files = list(Path(input_dir).glob(f'{group_id}*'))

            for file in group_files:
                to_remove.append(file)

    for file in to_remove:
        file.unlink(missing_ok=True)

    print(f"{len(to_remove) / 2} files removed due to broken audios.")


def smalliso(input_dir):
    """Remove small isolated annotations"""
    print("Removing too small isolated annotations...")
    waves = list(Path(input_dir).glob('*Isolated*.wav'))
    counter = 0
    for wav in list(waves):
        with contextlib.closing(wave.open(str(wav), 'r')) as open_wav:
            frames = open_wav.getnframes()
            rate = open_wav.getframerate()
            duration = frames / float(rate)
            if duration < 4:
                counter += 1
                lab = wav.parent / wav.with_suffix(".lab")
                wav.unlink()
                lab.unlink()
    print(f"{counter} files removed due to short duration.")


def final_clean(input_dir):
    p = Path(input_dir)
    for file in p.iterdir():
        if 'merged' not in file.name and 'Isolated' not in file.name:
            file.unlink()

        if 'Isolated' in file.name:
            if '.lab' in file.name:
                file.unlink()
            else:
                new_name = '_'.join(file.name.split(sep='_')[0:4]) + file.suffix
                file.rename(file.parent / new_name)


def remove_empties(input_dir):
    p = Path(input_dir)
    labs = sorted(list(p.glob('*.lab')))
    to_remove = []
    for lab in labs:
        if lab.stat().st_size == 0:
            if 'Isolated' in lab.name:
                group_id = '_'.join(lab.name.split(sep='_')[0:4])
            else:
                group_id = '_'.join(lab.name.split(sep='_')[0:3])

            group_files = list(Path(input_dir).glob(f'{group_id}*'))

            for file in group_files:
                to_remove.append(file)

    for file in to_remove:
        file.unlink(missing_ok=True)

if __name__ == "__main__":
    CHUNKS = sys.argv[1]
    OUTPUTS = sys.argv[2]
    empties(CHUNKS)
    broken_audios(CHUNKS)
    multiline(CHUNKS)
    punctwhite(CHUNKS)
    nonwords(CHUNKS, OUTPUTS)
    isoletter(CHUNKS)
    smalliso(CHUNKS)

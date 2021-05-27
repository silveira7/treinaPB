#!/usr/bin/env python3

from pathlib import Path
import string
import re
import enchant
import json


br = enchant.Dict('pt_BR')


def _get_labs(input_dir):
    """Get the list of .lab files"""
    labs = list(Path(input_dir).glob('*.lab'))
    return labs


def _get_waves(input_dir):
    """Get the list of .wav files"""
    waves = list(Path(input_dir).glob('*.wav'))
    return waves


def _delete_empties(input_dir):
    """Delete groups with empty labs"""
    print("Deleting empty .lab files...")
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


def _delete_broken_audios(input_dir):
    """Delete groups with broken audios"""
    print("Deleting broken .wav files...")
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


def _turn_one_line(input_dir):
    """???"""
    print("Fixing .lab files with more than one line...")
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


def _first_clean(input_dir):
    """Clean trascriptions in labs"""
    print("Cleaning transcriptions from puctations and extra spaces...")
    labs = _get_labs(input_dir)

    for lab in labs:
        with open(lab, 'r') as open_file:
            lines = open_file.readlines()

        # Remove punctations
        cleaned_string = lines[0].translate(
            str.maketrans('', '', string.punctuation))

        # Remove marginal whitespaces
        cleaned_string = cleaned_string.strip()

        # Remove duplicate whitespaces
        cleaned_string = re.sub(' +', ' ', cleaned_string)

        # Write cleaned file
        with open(lab, 'w') as opened_file:
            opened_file.write(cleaned_string)


def _check_words(input_dir, output_dir):
    """???"""
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

    non_words_json = json.dumps(non_words, indent=4)
    new_files_path = Path(output_dir)

    with open(new_files_path / "non_words.json", 'w') as opened_file:
        opened_file.write(non_words_json)


def _remove_isol_letter(input_dir):
    """???"""
    print("Checking transcriptions with isolated letters...")
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


def cleaner(input_dir, output_dir):
    """???"""
    _delete_empties(input_dir)
    _delete_broken_audios(input_dir)
    _turn_one_line(input_dir)
    _first_clean(input_dir)
    _check_words(input_dir, output_dir)
    _remove_isol_letter(input_dir)

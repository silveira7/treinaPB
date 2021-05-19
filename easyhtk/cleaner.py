from pathlib import Path
import string
import re
import enchant
import json

br = enchant.Dict('pt_BR')


def get_labs(input_dir):
    labs = list(Path(input_dir).glob('*.lab'))
    return labs


def delete_empties(labs, input_dir):
    """Delete groups with empty labs"""
    for lab in list(labs):
        if lab.stat().st_size == 0:
            group_id = '_'.join(lab.name.split(sep='_')[0:2])
            group_files = list(Path(input_dir).glob(f'{group_id}*'))
            for file in list(group_files):
                file.unlink(missing_ok=True)
                if file in labs:
                    labs.remove(file)


def clean(labs):
    """Clean trascriptions in labs"""
    for lab in labs:
        with open(lab, 'r') as open_file:
            lines = open_file.readlines()

        # Check if there is more than one line
        if len(lines) > 1:
            raise Exception(f'Error: The file {lab.name} has more than one line of text.')

        # Remove punctations
        cleaned_string = lines[0].translate(str.maketrans('', '', string.punctuation))

        # Remove marginal whitespaces
        cleaned_string = cleaned_string.strip()

        # Remove duplicate whitespaces
        cleaned_string = re.sub(' +', ' ', cleaned_string)

        # Write cleaned file
        with open(lab, 'w') as opened_file:
            opened_file.write(cleaned_string)


def check_words(labs):
    blank_files = []
    non_words = {}
    non_words_path = []
    for lab in labs:
        with open(lab, 'r') as open_file:
            line = open_file.readline()

        # Check if all words are Brazilian words
        word_list = line.split(sep=' ')

        for word in word_list:
            try:
                if not br.check(word.strip()):
                    non_words[lab.name] = word
                    if lab not in non_words_path:
                        non_words_path.append(lab)
            except ValueError:
                blank_files.append(lab.name)
                break
    return {'non-words': non_words, 'blank files': blank_files}


def export_files(non_words, blank_files, output_dir):
    # Write json with info about files with non-words
    non_words_json = json.dumps(non_words, indent=4)
    empty_files_json = json.dumps(blank_files, indent=4)
    new_files_path = Path(output_dir)

    with open(new_files_path / "non_words.json", 'w') as opened_file:
        opened_file.write(non_words_json)

    with open(new_files_path / "blank_files.json", 'w') as opened_file:
        opened_file.write(empty_files_json)


def remove_non_words(labs_path, input_dir):
    # Remove groups with non-words
    for file in labs_path:
        if 'Isolated' in file.name:
            group_id = '_'.join(file.name.split(sep='_')[0:5])
        else:
            group_id = '_'.join(file.name.split(sep='_')[0:4])
        group_files = list(Path(input_dir).glob(f'{group_id}*'))
        for group_file in group_files:
            group_file.unlink(missing_ok=True)

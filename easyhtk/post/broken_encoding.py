#!/usr/bin/env python3

"""Fix words with encoding error"""

import re
from pathlib import Path


def fix_encoding(input_dir):
    tgs = list(Path(input_dir).glob('*.TextGrid'))
    labs = list(Path(input_dir).glob('*.lab'))
    total = len(tgs)

    for index, tg in enumerate(tgs):
        print(f'{index} from {total}')
        for lab in labs:
            if tg.name[:-9] == lab.name[:-4]:
                with open(lab, 'r') as opened_file:
                    transcript = opened_file.readline().split()

        with open(tg, 'r') as opened_file:
            lines = opened_file.readlines()

        for index, line in enumerate(lines):
            if re.search(r'item \[2]:', line):
                tier_limit = index

        phon_tier = []
        word_tier = []

        for index, line in enumerate(lines):
            if index >= tier_limit:
                word_tier.append(line)
            else:
                phon_tier.append(line)

        counter = 0

        for index, line in enumerate(word_tier):

            text_line = re.compile(r'text =')
            in_quotes = re.compile(r'\".*\"')

            if text_line.search(line) and not re.search(r'\"sil\"|\"sp\"', line):
                try:
                    if in_quotes.search(line).group()[1:-1] != transcript[counter]:
                        word_tier[index] = in_quotes.sub('"' + transcript[counter] + '"', line)
                    counter += 1
                except IndexError:
                    pass

        new_tg = "".join(phon_tier + word_tier)
        with open(tg, 'w') as open_tg:
            open_tg.write(new_tg)

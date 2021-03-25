"""Fix words with encoding error"""

import os
import re
import glob


def fix_encoding(folder):
    os.chdir(folder)

    tg = glob.glob('*.TextGrid')
    lab = glob.glob('*.lab')

    for tg_file in tg:
        for lab_file in lab:
            if tg_file[:-9] == lab_file[:-4]:
                with open(lab_file, 'r') as opened_file:
                    transcript = opened_file.readline().split()
        with open(tg_file, 'r') as opened_file:
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
            if text_line.search(line) and not re.search(r'\"sil\"|\"sp\"', line):
                try:
                    if re.search(r'\".*\"', line).group()[1:-1] != transcript[counter]:
                        word_tier[index] = re.sub(r'\".*\"', '"' + transcript[counter] + '"', line)
                    counter += 1
                except IndexError:
                    pass
        new_tg = "".join(phon_tier + word_tier)
        new_file = open(tg_file, 'w')
        new_file.write(new_tg)
        new_file.close()

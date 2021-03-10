#!/usr/bin/env python3

"""This module automates the creation of VV tier from segment tier in TextGrids"""

import re
import copy    
import os
import sys

folder = sys.argv[1]
os.chdir(folder)
files = sorted(os.listdir(folder))

for file in files:
    print(file)
    if re.search('_merged.TextGrid', file):

        # Import TextGrid
        with open(file) as opened_file:
            tg = opened_file.readlines()

        # Determine beginning and end of 1st tier (phone tier)
        lower_limit = int()
        upper_limit = int()

        for line in tg:
            if re.search(r'item \[1]', line):
                lower_limit = tg.index(line)
            if re.search(r'item \[2]', line):
                upper_limit = tg.index(line)

        # Store only the 1st tier's intervals in a new variable
        phone_tier = copy.deepcopy(tg[lower_limit:upper_limit])

        vv_tier = copy.deepcopy(phone_tier[0:6])

        # Regex to identify characters representing consonantal sounds
        consonant = r'p|b|t|d|k|g|f|s|sh|v|z|zh|S|m|n|nh|r|R|l|lh|L'

        one_consonant_begin = False
        two_consonants_begin = False
        line_ignore = 9

        # Remove ""
        for index, value in enumerate(phone_tier):
            if re.search(r'\t\t\t\ttext = ""\n', value):
                del phone_tier[index-3:index+1]
                pass

        # Remove sil
        for index, value in enumerate(phone_tier):
            if index != 9 and re.search(r'\t\t\t\ttext = "sil"\n', value):
                del phone_tier[index-3:index+5]
                pass

        if re.search(consonant, phone_tier[13][12:-2]):
            one_consonant_begin = True
            line_ignore = 13
            if re.search(consonant, phone_tier[17][12:-2]):
                two_consonants_begin = True
                line_ignore = 17

        # Get the xmax of the first interval (silence)
        if one_consonant_begin:
            # xmax is equal to xmin of fourth interval (skip the two first consonants)
            if two_consonants_begin:
                first_max = phone_tier[19][11:-1]
            # xmax is equal to xmin of third interval (skip the first consonant)
            else:
                first_max = phone_tier[15][11:-1]
        else:
            first_max = phone_tier[8][11:-1]

        vv_tier = vv_tier + ['\t\t\tintervals [1]:\n',
                             '\t\t\t\txmin = 0.00\n',
                             '\t\t\t\txmax = ' + first_max + '\n',
                             '\t\t\t\ttext = "sil"\n']

        vv_units = []

        for index, value in enumerate(phone_tier):
            # Skip lines
            if index <= line_ignore:
                continue
            # If vowel
            elif re.search(r'text = ', value) and not re.search(consonant, value[12:-2]):
                try:
                    mod = 4
                    vv_unit = value[12:-2]
                    while re.search(consonant, phone_tier[index+mod][12:-2]):
                        vv_unit += phone_tier[index + mod][12:-2]
                        mod += 4
                    if mod / 4 == 1:
                        xmax = phone_tier[index+2][11:-1]
                    elif mod / 4 == 2:
                        xmax = phone_tier[index+6][11:-1]
                    elif mod / 4 == 3:
                        xmax = phone_tier[index+10][11:-1]
                    vv_tier = vv_tier + ['\t\t\tintervals [1]:\n',
                                         '\t\t\t\txmin = ' + phone_tier[index - 2][11:-1] + '\n',
                                         '\t\t\t\txmax = ' + xmax + '\n',
                                         '\t\t\t\ttext = "' + vv_unit + '"\n']
                except IndexError:
                    xmax = phone_tier[4][9:-1]
                    vv_tier = vv_tier + ['\t\t\tintervals [1]:\n',
                                         '\t\t\t\txmin = ' + phone_tier[index - 2][11:-1] + '\n',
                                         '\t\t\t\txmax = ' + xmax + '\n',
                                         '\t\t\t\ttext = "sil"\n']

        tg[6] = 'size = 3\n'

        # Update the number of the tier
        vv_tier[0] = '\titem [3]:\n'

        # Update the name of the tier
        vv_tier[2] = '\t\tname = "syllables"\n'

        size = 0

        # Update the number of the intervals
        for index, line in enumerate(list(vv_tier)):
            if re.search(r'intervals \[', line):
                size += 1
                vv_tier[index] = '\t\tintervals [' + str(size) + ']:\n'

        # Update the total number of intervals
        for index, line in enumerate(list(vv_tier)):
            if re.search(r'intervals: size =', line):
                vv_tier[index] = '\t\tintervals: size = ' + str(size) + '\n'

        final_tier = tg + vv_tier
        final_tier = ''.join(final_tier)

        new_tg = open(f'{folder}{file}', 'w')
        new_tg.write(final_tier.expandtabs(4))
        new_tg.close()

#!/usr/bin/env python3

"""This module automates the creation of VV tier from segment tier in TextGrids"""

import re
import copy
import os


def create_vv_tier(folder):

    os.chdir(folder)
    files = sorted(os.listdir(folder))

    for file in files:
        if 'merged.TextGrid' in file:
                # or ('Isolated' in file and '.TextGrid' in file):

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

            # Remove ""
            for index, value in enumerate(phone_tier):
                if re.search(r'\t\t\t\ttext = ""\n', value):
                    del phone_tier[index-3:index+1]
                    pass

            # Remove sil except the first
            for index, value in enumerate(phone_tier):
                if index != 9 and re.search(r'\"sil\"', value):
                    del phone_tier[index-3:index+5]
                    pass

            # Check if the tier starts with one or two consonants
            one_consonant_begin = False
            two_consonants_begin = False
            line_ignore = 9

            text = re.compile(r'\"(.*)\"')

            first_segment = re.search(text, phone_tier[13]).groups()[0]
            try:
                second_segment = re.search(text, phone_tier[17]).groups()[0]
            except IndexError:
                print(file)

            if re.search(consonant, first_segment):
                one_consonant_begin = True
                line_ignore = 13
                if re.search(consonant, second_segment):
                    two_consonants_begin = True
                    line_ignore = 17

            time = re.compile(r'\d+\.\d+')

            # Get the modified xmax of the first interval (silence)
            if one_consonant_begin:
                # xmax is equal to xmin of fourth interval (skip the two first consonants)
                if two_consonants_begin:
                    first_max = re.search(time, phone_tier[19]).group()
                # xmax is equal to xmin of third interval (skip the first consonant)
                else:
                    first_max = re.search(time, phone_tier[15]).group()
            else:
                first_max = re.search(time, phone_tier[8]).group()

            # Add the first sil interval to vv_tier
            vv_tier = vv_tier + ['\t\t\tintervals [1]:\n',
                                 '\t\t\t\txmin = 0.00\n',
                                 '\t\t\t\txmax = ' + first_max + '\n',
                                 '\t\t\t\ttext = "sil"\n']

            for index, value in enumerate(phone_tier):
                # Skip lines
                if index <= line_ignore:
                    continue
                # If vowel
                elif re.search(r'text = ', value):
                    segment = re.search(text, value).group()[1:-1]
                    if not re.search(consonant, segment):
                        try:
                            mod = 4
                            unit_add = re.search(text, phone_tier[index + mod]).group()[1:-1]
                            while re.search(consonant, unit_add):
                                segment += unit_add
                                mod += 4
                                unit_add = re.search(text, phone_tier[index + mod]).group()[1:-1]
                            if mod / 4 == 2:
                                xmax = re.search(time, phone_tier[index + 6]).group()
                            elif mod / 4 == 3:
                                xmax = re.search(time, phone_tier[index + 10]).group()
                            elif mod / 4 == 4:
                                xmax = re.search(time, phone_tier[index + 14]).group()
                            elif mod / 4 == 5:
                                xmax = re.search(time, phone_tier[index + 18]).group()
                            else:
                                xmax = re.search(time, phone_tier[index + 2]).group()

                            xmin = re.search(time, phone_tier[index-2]).group()

                            vv_tier = vv_tier + ['\t\t\tintervals [1]:\n',
                                                 '\t\t\t\txmin = ' + xmin + '\n',
                                                 '\t\t\t\txmax = ' + xmax + '\n',
                                                 '\t\t\t\ttext = "' + segment + '"\n']
                        except IndexError:
                            xmax = re.search(time, phone_tier[4]).group()
                            xmin = re.search(time, phone_tier[index - 2]).group()
                            vv_tier = vv_tier + ['\t\t\tintervals [1]:\n',
                                                 '\t\t\t\txmin = ' + xmin + '\n',
                                                 '\t\t\t\txmax = ' + xmax + '\n',
                                                 '\t\t\t\ttext = "sil"\n']

            tg[6] = 'size = 3\n'

            # Update the number of the tier
            vv_tier[0] = '\titem [2]:\n'

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

            tg[upper_limit] = '\titem [3]:\n'

            final_tier = tg[:upper_limit] + vv_tier + tg[upper_limit:]

            final_tier = ''.join(final_tier)

            new_tg = open(f'{folder}{file}', 'w')
            new_tg.write(final_tier.expandtabs(4))
            new_tg.close()

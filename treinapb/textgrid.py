"""This module merges the .TextGrid files of the same group of annotations"""

import re
import os
import sys
import copy
from pathlib import Path


# TODO Inserir variável posição do índice de grupo no nome do arquivo

class TextGrid:
    """A class to store and manipulate .TextGrid data"""

    def __init__(self, folder):

        # Store the folder
        self.folder = folder

        # print('Getting list of files...')
        # Store the name of all files .TextGrid
        text_grids = sorted(os.listdir(self.folder))

        self.files = []

        # print('Getting list of TextGrid files')
        for file in text_grids:
            if 'TextGrid' in file and 'merged' not in file:
                self.files.append(file)

        # Dict to store the content of each TextGrid
        self.data = dict()

        # Dict to store the merged TextGrid
        self.final_tg = dict()

    def get_metadata(self):
        """This function stores TextGrid data in an organized way"""

        # The outcome of this loop is a structure like this:
        # {'ALCP_2017FA+_AdrieleS': {'0': ['ALCP_2017FA+_AdrieleS_0_a46_68743_74269.TextGrid']}}
        # This loop gets the following structured information:
        # Speaker:
        #     Group ID:
        #         List of the name of files of the group
        # This loop
        print('Getting info from filename...')
        for file in self.files:
            if 'Isolated' not in file:
                # Get the first four information of file name (corpus, social profile, speaker's name and group ID)
                # and store it as a string with underscores
                speaker = "_".join(file.split(sep='_')[:2])
                # Store the group ID
                group = file.split(sep='_')[2]
                # If the speaker of current file is not yet in self.data...
                if speaker not in self.data.keys():
                    # Add speaker to data
                    self.data[speaker] = {group: [file]}
                    # And to final_tg
                    self.final_tg[speaker] = {group: []}
                # If speaker of current file is already in data...
                else:
                    # If the group of current file is not in the groups of speaker
                    if group not in self.data[speaker].keys():
                        # Add the group to the groups of speaker
                        self.data[speaker][group] = [file]
                        self.final_tg[speaker][group] = []
                    # If the group is already in the groups of speaker
                    # just append the current file to the files of the group
                    else:
                        self.data[speaker][group].append(file)

        attrib = []  # Ex.: ['2', '0.12', '0.17', 'p']
        intervals = []  # Ex.: [['1', '0.0', '0.12', 'sil'], ['2', '0.12', '0.17', 'p'], ...]
        tiers = []  # A list with two intervals like above
        # For each file in each group of each speaker...
        for speaker in self.data.copy().keys():

            xmax = 0
            for group in self.data.copy()[speaker]:
                for file in self.data.copy()[speaker][group]:

                    # Open the file
                    with open(os.path.join(self.folder, file)) as opened_file:
                        tmp = opened_file.readlines()
                        # Increment xmax of current file to xmax of group
                        for line in tmp:
                            if re.search(r'xmax', line):
                                xmax += float(line[7:-1])
                                break
                        # Get the line that separates the tiers
                        for line in tmp:
                            if re.search(r'item \[2]', line):
                                tier_limit = tmp.index(line)

                        # Create a list with the lines of 1st tier
                        first_tier = tmp[:tier_limit]
                        # Create a list with the lines of 2nd tier
                        second_tier = tmp[tier_limit:]
                        # For each line of each tier...
                        for tier in [first_tier, second_tier]:
                            for index, line in enumerate(tier):
                                # For each interval
                                if re.search(r'intervals \[', line):
                                    attrib.append(re.search(r'\d+', line).group())  # Interval number
                                    attrib.append(re.search(r'\d+\.\d+', tier[index + 1]).group())  # Begin time
                                    attrib.append(re.search(r'\d+\.\d+', tier[index + 2]).group())  # End time
                                    attrib.append(re.search(r'\".*\"', tier[index+3]).group()[1:-1])  # Text
                                    # Example of attrib: ['2', '0.12', '0.17', 'p']
                                    intervals.append(attrib)  # Append attrib list to intervals list
                                    attrib = []  # Clear attrib list
                            # Append intervals list to tiers list
                            # Example of intervals:
                            # [['1', '0.0', '0.12', 'sil'], ['2', '0.12', '0.17', 'p'], ...]
                            tiers.append(intervals)
                            intervals = []  # Clear intervals

                        # Remembering the structure of self.data:
                        # {'ALCP_2017FA+_AdrieleS': {'0': ['ALCP_2017FA+_AdrieleS_0_a46_68743_74269.TextGrid', ...]}}
                        # Get the index of the file in the list of files of the group
                        index = self.data.copy()[speaker][group].index(file)
                        # Replace the name of the file by the tiers list (with the two tiers contents)
                        self.data[speaker][group][index] = tiers
                        # Clear tiers list
                        tiers = []

    def build_tg(self):
        tier_1 = []  # Store the strings of 1st tier
        tier_2 = []  # Store the strings of 2nd tier
        final = ''
        print('Building TextGrid')
        # For each tier in each file in each group of each speaker
        for speaker in self.data.copy().keys():
            for group in self.data.copy()[speaker]:
                xmax_1 = 0  # Variable to update the xmax of intervals of 1st tier
                xmax_2 = 0  # Variable to update the xmax of intervals of 2nd tier
                x = 1  # Variable to update interval number of 1st tier
                y = 1  # Variable to update interval number of 2nd tier
                for file in self.data.copy()[speaker][group]:

                    for index, tier in enumerate(file):
                        # If 1st tier
                        if index == 0:
                            # For each interval in 1st tier
                            for interval in tier:
                                interval = '\t\t\tintervals [' + str(x) + ']:\n' \
                                           + '\t\t\t\txmin = ' + str(
                                    "{:.2f}".format(float(interval[1]) + xmax_1)) + '\n' \
                                           + '\t\t\t\txmax = ' + str(
                                    "{:.2f}".format(float(interval[2]) + xmax_1)) + '\n' \
                                           + '\t\t\t\ttext = "' + str(interval[3]) + '"\n'

                                tier_1.append(interval)
                                x += 1
                            xmax_1 += float(file[0][-1][2])

                        # If 2nd tier
                        if index == 1:
                            # For each interval in 2nd tier
                            for interval in tier:
                                interval = '\t\t\tintervals [' + str(y) + ']:\n' \
                                           + '\t\t\t\txmin = ' + str(
                                    "{:.2f}".format(float(interval[1]) + xmax_2)) + '\n' \
                                           + '\t\t\t\txmax = ' + str(
                                    "{:.2f}".format(float(interval[2]) + xmax_2)) + '\n' \
                                           + '\t\t\t\ttext = "' + str(interval[3]) + '"\n'
                                y += 1
                                tier_2.append(interval)
                            xmax_2 += float(file[0][-1][2])

                header = 'File type = "ooTextFile"\n' \
                         + 'Object class = "TextGrid"\n' \
                         + '\n' \
                         + 'xmin = 0.0\n' \
                         + 'xmax = ' + str("{:.2f}".format(xmax_1)) + '\n' \
                         + 'tiers? <exists>\n' \
                         + 'size = 2\n' \
                         + 'item []:\n'

                first_tier_header = '\titem [1]:\n' \
                                    + '\t\tclass = "IntervalTier"\n' \
                                    + '\t\tname = "phones"\n' \
                                    + '\t\txmin = 0.0\n' \
                                    + '\t\txmax = ' + str("{:.2f}".format(xmax_1)) + '\n' \
                                    + '\t\tintervals: size = ' + str(len(tier_1)) + '\n'

                second_tier_header = '\titem [2]:\n' \
                                     + '\t\tclass = "IntervalTier"\n' \
                                     + '\t\tname = "words"\n' \
                                     + '\t\txmin = 0.0\n' \
                                     + '\t\txmax = ' + str("{:.2f}".format(xmax_1)) + '\n' \
                                     + '\t\tintervals: size = ' + str(len(tier_2)) + '\n'

                # Add main header to final string
                final += header

                # Add 1st tier header to final string
                final += first_tier_header

                # Add intervals of 1st tier to final string
                for x in tier_1:
                    final += x

                # Clear tier_1
                tier_1 = []

                # Add 2nd tier header to final string
                final += second_tier_header

                # Add intervals of 2nd tier to final string
                for x in tier_2:
                    final += x

                # Clear tier_2
                tier_2 = []

                # Export final file
                final_file = open(self.folder + "/" + speaker + "_"
                                  + group + '_merged.TextGrid', "w")
                final_file.write(final)
                final_file.close()
                final = ''

                if os.stat(self.folder + "/" + speaker + "_" + group + '_merged.TextGrid')[6] > 10**6:
                    print("File is too large")
                    sys.exit(1)


def create_vv_tier(folder):

    # os.chdir(folder)
    files = sorted(os.listdir(folder))

    for file in files:
        if ('Isolated' in file or 'merged' in file) and '.TextGrid' in file:
        #if 'merged.TextGrid' in file:
            # print(file)
                # or ('Isolated' in file and '.TextGrid' in file):

            # Import TextGrid
            with open(os.path.join(folder, file)) as opened_file:
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

            new_tg = open(os.path.join(folder, file), 'w')
            new_tg.write(final_tier.expandtabs(4))
            new_tg.close()


def fix_encoding(input_dir):
    tgs = list(Path(input_dir).glob('*.TextGrid'))
    labs = list(Path(input_dir).glob('*.lab'))
    total = len(tgs)
    print("Fixing enconding...")

    for index, tg in enumerate(tgs):
 # print(f'{index} from {total}')
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

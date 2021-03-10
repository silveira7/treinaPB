#!/usr/bin/env python3

"""This module merges the .TextGrid files of the same group of annotations"""

import re
import os


class TextGrid:
    """A class to store and manipulate .TextGrid data"""

    def __init__(self, folder):

        # Store the folder
        self.folder = folder

        # Store the name of all files .TextGrid
        text_grids = sorted(os.listdir(self.folder))
        self.files = [file for file in text_grids
                      if re.search(r'.TextGrid', file)]

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
        for file in self.files:
            # Get the first four information of file name (corpus, social profile, speaker's name and group ID)
            # and store it as a string with underscores
            speaker = "_".join(file.split(sep='_')[:3])
            # Store the group ID
            group = file.split(sep='_')[3]
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
                                    attrib.append(line[14:-3])  # Interval number
                                    attrib.append(tier[index + 1][11:-1])  # Begin time
                                    attrib.append(tier[index + 2][11:-1])  # End time
                                    attrib.append(tier[index + 3][12:-2])  # Text
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

        # For each tier in each file in each group of each speaker
        for speaker in self.data.copy().keys():
            for group in self.data.copy()[speaker]:
                xmax_1 = 0  # Variable to update the xmax of intervals of 1st tier
                xmax_2 = 0  # Variable to update the xmax of intervals of 2nd tier
                x = 1  # Variable to update interval number of 1st tier
                y = 1  # Variable to update interval number of 2nd tier
                for file in self.data.copy()[speaker][group]:
                    for index, tier in enumerate(file):
                        # print(index, tier)

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

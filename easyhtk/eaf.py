import os
import re
import sys
from datetime import datetime
import xml.etree.ElementTree as ElementTree
from pydub import AudioSegment
import prettify_xml


class Eaf:
    """Store information about annotation tiers from EAF files"""
    def __init__(self, path):
        self.path = path  # Path to the eaf/xml file
        self.time_order = {}  # TIME_SLOT_ID: TIME_VALUE
        self.tiers = {}  # ANNOTATION_ID: {TIME_SLOT_REF1, TIME_SLOT_REF2, ANNOTATION_VALUE, ...}
        self.annotations = {}  # Transition variable used only to build tiers dict
        self.overlapped = {}  # Store annotations of a reference tier that overlaps with annotations of other tiers
        self.not_overlapped = {}  # The opposite of the variable above
        self.no_gaps = {}  # Store annotations with no gaps when they are in clusters
        self.no_smalls = {}  # Store only annotations or clusters of annotations with more than a specified duration
        self.grouped = {}  # Copy from no_small, but with added information of group membership of each annotation
        self.groups = {}  # Store information about groups of annotations
        self.big_groups = []  # Store the IDs of big groups

        # Get the XML structure and store it in root
        self.tree = ElementTree.parse(path)
        self.root = self.tree.getroot()

        # Store the pairs with TIME_SLOT_ID and TIME_VALUE in time_order dict
        for child in self.root.find('TIME_ORDER'):
            self.time_order[child.attrib.get('TIME_SLOT_ID')] = child.attrib.get('TIME_VALUE')

        # Store the pairs with annotation IDs and associated information in tiers dict
        # The structure of the tiers dict is the following:
        # {annotation ID: {begin_time_slot: x, end_time_slot: y, annotation_value: z}}
        for child in self.root.findall('TIER'):
            # For each tier, loop each annotation of the tier
            for sub_child in child.findall('ANNOTATION'):
                self.annotations[sub_child[0].attrib.get('ANNOTATION_ID')] = {
                        'begin_time_slot': sub_child[0].attrib.get('TIME_SLOT_REF1'),
                        'end_time_slot': sub_child[0].attrib.get('TIME_SLOT_REF2'),
                        'annotation_value': sub_child[0][0].text
                        }
            self.tiers[child.attrib.get('TIER_ID')] = self.annotations
            self.annotations = {}

        # This loop adds more information to tiers dict
        # From begin_time_slot and end_time_slot, it identifies and stores the
        # corresponding values in milliseconds and in H:M:S.f format
        # Loop each tier
        for key in self.tiers.keys():
            # Loop each annotation of the tier
            for sub_key in self.tiers[key].keys():
                # Store begin_time_value in milliseconds
                self.tiers[key][sub_key]['begin_time_value'] = int(
                    self.time_order[self.tiers[key][sub_key]['begin_time_slot']])

                # Store end_time_value in milliseconds
                self.tiers[key][sub_key]['end_time_value'] = int(
                    self.time_order[self.tiers[key][sub_key]['end_time_slot']])

                # Store duration in milliseconds
                self.tiers[key][sub_key]['duration'] = int(
                    self.tiers[key][sub_key]['end_time_value']) - int(
                    self.tiers[key][sub_key]['begin_time_value'])

                # Store begin_time_value_formatted in H:M:S.f format
                self.tiers[key][sub_key]['begin_time_value_formatted'] = datetime.utcfromtimestamp(
                    self.tiers[key][sub_key]['begin_time_value']/1000).strftime('%H:%M:%S.%f')

                # Store end_time_value_formatted in H:M:S.f format
                self.tiers[key][sub_key]['end_time_value_formatted'] = datetime.utcfromtimestamp(
                    self.tiers[key][sub_key]['end_time_value']/1000).strftime('%H:%M:%S.%f')

    def show_annotations(self, tier):
        """Organized display of information of all annotations of a tier"""
        for annotation in self.tiers[tier]:
            print("Begin: " + self.tiers[tier][annotation]['begin_time_value_formatted'] + "\n" +
                  "End: " + self.tiers[tier][annotation]['end_time_value_formatted'] + "\n" +
                  "Duration: " + str(self.tiers[tier][annotation]['duration']) + "\n" +
                  "Content: " + '"' + self.tiers[tier][annotation]['annotation_value'] + '"' + "\n"
                  )

    def remove_overlaps(self, reference_tier, exceptions):
        """Get all annotations of a tier that do not overlap with annotations of other tiers"""
        selected_tiers = []  # To store the selected tier from reference_tier and exceptions
        temp = {}  # Transitory variable to build the intervals dict
        intervals = {}  # {each tier: {begin: end, begin: end, ...}}

        # Store in a list the name of the tiers selected by the user
        for tier in self.tiers.keys():
            if tier not in exceptions:
                selected_tiers.append(tier)
            else:
                continue

        # Store in a dict the pair with begin and end time (in milliseconds) of each annotation of each selected tier
        for tier in selected_tiers:
            for attrib in self.tiers[tier].values():
                temp[attrib['begin_time_value']] = attrib['end_time_value']
            intervals[tier] = temp
            temp = {}

        # Check if intervals of reference tier overlap with intervals of other tiers
        # Loop through intervals of reference tier
        for ref_tier_interval_begin, ref_tier_interval_end in intervals[reference_tier].items():
            # Restrict to selected tiers that are not the reference tier
            for other_tier in selected_tiers:
                out = False  # Boolean variable used to get out of nested loops
                if other_tier != reference_tier:
                    for other_tier_interval_begin,  other_tier_interval_end in intervals[other_tier].items():
                        # Check if the interval of reference tier overlaps with at least one interval
                        # of another tier
                        if ref_tier_interval_begin <= other_tier_interval_end and \
                                other_tier_interval_begin <= ref_tier_interval_end:
                            # If so, store the interval and get out of the loop
                            self.overlapped[ref_tier_interval_begin] = ref_tier_interval_end
                            out = True
                            break  # Go out of the inner loop
                        else:
                            continue
                else:
                    continue
                if out:
                    break  # Go out of the outer loop

        # From overlapped intervals, get a dict with information of not overlapped annotations
        for annotation, attrib in self.tiers[reference_tier].items():
            # Check if interval is not overlapped
            if (attrib['begin_time_value'] not in self.overlapped) and \
                    (attrib['end_time_value'] not in self.overlapped):
                # Store the attributes of not overlapped annotations
                self.not_overlapped[annotation] = [
                    attrib['begin_time_value'],
                    attrib['end_time_value'],
                    attrib['duration'],
                    attrib['annotation_value']]
            else:
                continue

    def remove_gaps(self, reference):
        """Remove gaps between annotations that form a cluster"""

        # Store list of attributes of not overlapped annotations
        reference_tier = list(self.not_overlapped.values())
        # Store list of IDs of not overlapped annotations
        annotation_id = list(self.not_overlapped.keys())
        # To store the begin time of all annotations of the others tiers (not ref tier)
        other_tiers_begins = list()

        # Use of meaningful words in place of numerical index
        begin = 0
        end = 1
        duration = 2

        def normal_values():
            """Store in no_gaps the regular begin, end and duration of the annotation"""
            self.no_gaps[annotation_id[index]] = reference_tier[index]

        def modified_values():
            """Store in no_gaps the regular begin, but modified end and duration of the annotation"""
            # The end of the current annotation is set to be the same as the beginning of the next annotation
            modified_duration = reference_tier[index+1][begin] - reference_tier[index][begin]
            self.no_gaps[annotation_id[index]] = reference_tier[index]
            self.no_gaps[annotation_id[index]][end] = reference_tier[index+1][begin]
            self.no_gaps[annotation_id[index]][duration] = modified_duration

        # Create a list with the begin time value of all intervals of other tiers
        for tier, annotation in self.tiers.items():
            if tier != reference:
                for attrib in annotation.values():
                    if attrib['begin_time_value'] not in other_tiers_begins:
                        other_tiers_begins.append(attrib['begin_time_value'])
                    else:
                        continue
            else:
                continue

        # Loop to remove time gaps inside clusters of annotations
        for index in range(len(reference_tier)-1):
            # Check if the annotation has 2 seconds or less
            if reference_tier[index][duration] <= 2000:
                # Check if the gap between the current annotation and the next is larger than 1,5 second
                if reference_tier[index+1][begin] - reference_tier[index][end] > 1500:
                    # Check if the gap between the current annotation and the previous one is larger than 1,5 second
                    if reference_tier[index][begin] - reference_tier[index-1][end] > 1500:
                        continue  # If true, do not store this annotation
                    else:
                        # If false, store the annotation with regular values
                        normal_values()
                else:
                    # If annotation is closer to the next with less than 1,5 second
                    obstacle = False
                    for time_value in other_tiers_begins:
                        # Check if there is some annotation between
                        # the gap separating participant's annotation and the following
                        if reference_tier[index][end] <= time_value <= reference_tier[index+1][begin]:
                            obstacle = True
                        else:
                            continue
                    # If there is an annotation in between
                    if obstacle:
                        normal_values()
                    # If there is not
                    else:
                        modified_values()
            else:
                # If the annotation has more than 2 seconds, check if the gap between the annotation
                # and the next is larger than 1 second and a half
                if reference_tier[index+1][begin] - reference_tier[index][end] > 1500:
                    normal_values()
                else:
                    # If the gap between the current annotation and the next is less than 1,5 second
                    # Check if there is an annotation in between
                    obstacle = False
                    for time_value in other_tiers_begins:
                        if reference_tier[index][end] <= time_value <= reference_tier[index+1][begin]:
                            obstacle = True
                        else:
                            continue
                    # If there is an annotation in between
                    if obstacle:
                        normal_values()
                    # If there is not
                    else:
                        modified_values()

    def remove_small_clusters(self):
        """Remove isolated annotations or clusters of annotations that have less than 2 seconds"""
        reference_values = list(self.no_gaps.values())
        annotation_ids = list(self.no_gaps.keys())
        overlapped_values = list()
        overlapped_ids = list()

        # Meaningful words in place of index number
        begin = 0
        end = 1
        duration = 2

        # Loop with range according to number of annotations of reference tier less four
        for index in range(len(reference_values) - 10):
            mod1 = 0
            mod2 = 1
            contiguous = False
            large_enough = False
            # Check if annotation finishes where the next begins
            while reference_values[index+mod1][end] == reference_values[index+mod2][begin]:
                contiguous = True
                # Check if the annotation and the next together lasts for more than 2 seconds
                if reference_values[index+mod2][end] - reference_values[index][begin] >= 4000:
                    large_enough = True
                    break
                else:
                    mod1 += 1
                    mod2 += 1
            # If annotation is not side-by-side to the next
            if not contiguous:
                # If it lasts for more than 2 seconds, does not do nothing
                if reference_values[index][duration] >= 4000:
                    continue
                # If its beginning is the end of the previous annotation, does not do nothing
                elif reference_values[index][begin] == reference_values[index-1][end]:
                    continue
                # Else, delete the current annotation from annotation_id and reference_tier lists
                else:
                    overlapped_values.append(reference_values[index])
                    overlapped_ids.append(annotation_ids[index])
            # If it's contiguous to the next, but both does not sums up more than 2 seconds
            elif not large_enough:
                # If its beginning is the end of the previous annotation, does not do nothing
                if reference_values[index][begin] == reference_values[index-1][end]:
                    continue
                # Else, delete current annotation from annotation_id and reference_tier lists
                else:
                    for x in range(mod2):
                        overlapped_values.append(reference_values[index+x])
                        overlapped_ids.append(annotation_ids[index+x])

        # Store the remaining annotations in no_small dict
        for index in range(len(annotation_ids)):
            if annotation_ids[index] not in overlapped_ids:
                self.no_smalls[annotation_ids[index]] = reference_values[index]
            else:
                continue

    def write_eaf(self, ref_tier_id):
        """Write a new EAF/XML file"""
        # This function writes a new EAF/XML file with the original tiers and a new tier comprising the annotations
        # filtered by the functions remove_overlaps, remove_gaps and remove_small_clusters
        new_tier_id = ref_tier_id + " Modified"  # Store the ID for the new tier
        reference_tier = []  # Store begin and end time values
        annotation_id = []  # Store the annotation IDs
        all_annotations_id = []  # Store all original annotations IDs

        # Store begin and end time values
        for values in self.no_smalls.values():
            reference_tier.append(values[:])

        # Store all original annotations IDs
        for tier in self.tiers.values():
            for annotation in tier.keys():
                all_annotations_id.append(int(annotation[1:]))

        # Get the highest annotation ID
        highest_id = max(all_annotations_id)

        # Create a list with the annotations IDs for the new tier
        add = 1
        for index in range(len(reference_tier)):
            annotation_id.append("a" + str(highest_id + add))
            add += 1

        # Replace time values for matching time slot IDs
        for index in range(len(reference_tier)):
            for key, value in self.time_order.items():
                if reference_tier[index][0] == int(value):
                    reference_tier[index][0] = key
                elif reference_tier[index][1] == int(value):
                    reference_tier[index][1] = key
                else:
                    continue

        # Add a new TIER element in XML tree and attributes
        ElementTree.SubElement(self.root, 'TIER',
                               attrib={
                                   'LINGUISTIC_TYPE_REF': 'default-lt',
                                   'TIER_ID': new_tier_id})

        # Add inner elements to the just created TIER element
        for index in range(len(reference_tier)):
            # Add ANNOTATION elements
            ElementTree.SubElement(self.root.findall('TIER')[-1], 'ANNOTATION')
            # Add ALIGNABLE_ANNOTATION elements and attributes
            ElementTree.SubElement(
                self.root.findall('TIER')[-1].findall('ANNOTATION')[-1],
                'ALIGNABLE_ANNOTATION',
                attrib={
                    'ANNOTATION_ID': annotation_id[index],
                    'TIME_SLOT_REF1': reference_tier[index][0],
                    'TIME_SLOT_REF2': reference_tier[index][1]
                    }
            )
            # Add ANNOTATION_VALUE elements
            ElementTree.SubElement(
                 self.root.findall(
                     'TIER')[-1].findall(
                     'ANNOTATION')[-1].find(
                     'ALIGNABLE_ANNOTATION'),
                 'ANNOTATION_VALUE'
            )
            # Add text to ANNOTATION_VALUE elements
            self.root.findall(
                'TIER')[-1].findall(
                'ANNOTATION')[-1].find(
                'ALIGNABLE_ANNOTATION').find(
                'ANNOTATION_VALUE').text = reference_tier[index][3]

        # Fix the format of the new XML/EAF code
        prettify_xml.indent(self.root)

        # Create directory for eaf files
        try:
            os.mkdir('eaf_files')
        except FileExistsError:
            pass

        # Write the new XML/EAF file using UTF-8 encoding
        filename = re.split("/", self.path)[-1][:-4] + '_New' + '.eaf'
        path = 'eaf_files/' + filename
        if os.path.exists(path):
            print('Error: File' + ' "' + filename + '" ' + 'already exists!')
            sys.exit(1)
        else:
            self.tree.write(path, encoding="utf-8")

    def create_grouped(self):
        """Create groups of annotations with duration ranging between four and eight seconds"""
        no_smalls_copy = dict()
        no_smalls_list = list()

        # Create a copy of no_small dict
        for key, value in self.no_smalls.items():
            no_smalls_copy[key] = value.copy()

        # Turn the copy into nested lists
        for key, value in no_smalls_copy.items():
            value.insert(0, key)
            no_smalls_list.append(value.copy())

        # Variables created only to make the following loop more readable
        begin = 1
        end = 2
        group_num = 0

        for annotation in no_smalls_list:
            # If annotation is the first of the list
            if annotation == no_smalls_list[0]:
                # Store the next annotation parameters
                next_annotation = no_smalls_list[no_smalls_list.index(annotation) + 1]
                # If current annotation's end matches next annotation's begin
                if annotation[end] == next_annotation[begin]:
                    # Insert group_num in the 2nd position
                    annotation.insert(1, group_num)
                # Else, insert the value 'Isolated' and do not update group_num
                # since it was not used for current annotation
                else:
                    annotation.insert(1, 'Isolated')
            # If annotation is the last of the list
            elif annotation == no_smalls_list[-1]:
                # Store the previous annotation parameters
                previous_annotation = no_smalls_list[no_smalls_list.index(annotation) - 1]
                # If current annotation's begin matches previous annotation's end
                if annotation[begin] == previous_annotation[end + 1]:
                    # Insert group_num in 2nd position
                    annotation.insert(1, group_num)
                # Else, insert the value 'Isolated' and do not update group_num
                else:
                    annotation.insert(1, 'Isolated')
            # If annotation is not the first nor the last
            else:
                # Stores the previous annotation's parameters
                previous_annotation = no_smalls_list[no_smalls_list.index(annotation) - 1]
                # Stores the next annotation's parameters
                next_annotation = no_smalls_list[no_smalls_list.index(annotation) + 1]
                # If current annotation's end matches next annotation's begin
                if annotation[end] == next_annotation[begin]:
                    # Insert group_num in 2nd position
                    annotation.insert(1, group_num)
                # If current annotation's begin matches previous annotation's end
                elif annotation[begin] == previous_annotation[end + 1]:
                    # Insert group_num in 2nd position
                    annotation.insert(1, group_num)
                    # Update group_num since the annotation is the last of the current group
                    group_num += 1
                # Else, insert 'Isolated' and do not update group_num
                else:
                    annotation.insert(1, 'Isolated')

        # Turn no_smalls_list into a dictionary with the same organization as no_smalls_dicts
        # but with added information of group membership for each annotation
        # {annotation_id: [group_id, begin, end, duration, transcription]}
        for annotation in no_smalls_list:
            self.grouped[annotation[0]] = annotation[1:]

    def create_groups(self):
        """Create dict that stores information about groups of annotations"""
        ids = set()  # Stores group IDs

        # Create a set of all group IDs
        for value in self.grouped.values():
            ids.add(value[0])

        # Create the structure of groups dict: {id_number: [ duration, [annotations' IDs] ]}
        for id_number in ids:
            self.groups[id_number] = [0, []]

        # Stores group information in groups dict
        for key, value in self.grouped.items():
            for key_1, value_1 in self.groups.items():
                if value[0] == key_1:
                    value_1[0] += value[3]
                    value_1[1].append(key)

    def slipt(self):
        """Split groups larger than 12 seconds into two smaller groups"""

        # big_groups = list()  # Stores the IDs of big groups (larger than 12 seconds)
        split = False  # Boolean variable to check if annotation was split or not
        new_group_duration = None  # Temp. variable to store the duration of the new group
        annotations = list()   # Temp. variable to store the annotations' ID of th

        # Variables to make the following code more readable
        begin = 1
        end = 2

        # Loop to split big groups
        for each_big_group in self.big_groups:
            # For each big group, loop into all groups
            for group_id, parameters in self.groups.items():
                # If current big group matches the group in groups dict
                if each_big_group == group_id:
                    x = 1  # Index to loop into annotations that are members of current big group
                    # Loop into current big group's annotations until the sum of their durations reach 8 seconds
                    # or until reach the last annotation
                    while x < len(parameters[1]) and \
                            self.grouped[parameters[1][x]][end] - self.grouped[parameters[1][0]][begin] < 8000:
                        x += 1
                    # If reach 8 seconds
                    if x < len(parameters[1]):
                        # Set split as true, clear annotations list and
                        split = True
                        annotations = list()
                        # Store the joint duration of the remaining annotations (those that was
                        # no considered in previous while loop)
                        new_group_duration = self.grouped[
                                                 parameters[1][len(parameters[1]) - 1]
                                             ][end] - self.grouped[parameters[1][x]][begin]
                        # Insert each remaining annotation into regrouped_annotations
                        while x < len(parameters[1]):
                            annotations.append(parameters[1][x])
                            x += 1
                        # For each regrouped annotation
                        for annotation in annotations:
                            # Remove it from its original group
                            self.groups[group_id][1].remove(annotation)
                            # Update its group ID in grouped dict
                            self.grouped[annotation][0] = len(self.groups) + 1
                        # Update the duration of the original group since it was split
                        self.groups[group_id][0] = self.groups[group_id][0] - new_group_duration
                    else:
                        continue
                else:
                    continue
            # If current group was split, insert the group's information in groups dict
            if split:
                self.groups[len(self.groups) + 1] = [new_group_duration, annotations, each_big_group]
                split = False

    def split_iter(self):
        """Iterates split function until there is no more big groups"""
        self.create_grouped()
        self.create_groups()

        while True:
            # Check if there is at least one group that lasts more than 12 seconds
            for key, value in self.groups.items():
                if key != "Isolated" and value[0] > 8000:
                    if (value[0] - 8000) > 4000:
                        self.big_groups.append(key)
                else:
                    continue
            # If there isn't, stop the loop
            if not self.big_groups:
                break
            # Else (if there is), run split function
            else:
                self.slipt()
                self.big_groups = list()  # Clear big_groups list before running the next loop

    def get_number_of_groups(self):
        """Return the number of groups"""
        number = len(self.groups)
        return number

    def extract_audio(self, audio_source):
        """Extract and write the WAV file for each annotation and a TXT file with the annotation's content"""

        # Import WAV file
        audio = AudioSegment.from_wav(audio_source)

        # Create subdir in output for each audio source
        path = 'media_files'
        try:
            os.makedirs(path)
        except FileExistsError:
            pass

        # Variables to make code more readable
        group_id = 0
        begin = 1
        end = 2
        content = 4

        # Set the path to the audio
        source_name = re.split('/', audio_source)[-1][:-4]

        # Slice and write the WAV file for each annotation
        for annotation_id, parameter in self.grouped.items():
            # Slice the interval of the annotation
            audio_cut = audio[parameter[begin]:parameter[end]]
            # Convert stereo to mono
            audio_cut = audio_cut.set_channels(1)
            # Set sampling rate to 16.000 Hz (the default for HTK models)
            audio_cut = audio_cut.set_frame_rate(16000)
            # Define the name of the audio file
            filename = source_name + "_" \
                + str(parameter[group_id]).zfill(3) + "_" \
                + str(annotation_id) + "_" \
                + str(parameter[begin]) + "_" \
                + str(parameter[end]) + ".wav"
            # Export the audio as WAV using PCM signed 16-bit little-endian (ffmpeg)
            audio_cut.export(path + "/" + filename, format='wav', codec='pcm_s16le')

        # Write a TXT file for each annotation, with the annotation content
        for annotation_id, parameter in self.grouped.items():
            # Define the name of the transcription file
            filename = source_name + "_" \
                + str(parameter[group_id]).zfill(3) + "_" \
                + str(annotation_id) + "_" \
                + str(parameter[begin]) + "_" \
                + str(parameter[end]) + ".lab"
            # Write the transcription file in the same folder
            file_created = open(path + "/" + filename, "w")
            file_created.write(parameter[content].lower())
            file_created.close()

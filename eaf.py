import os
from datetime import datetime
import xml.etree.ElementTree as ElementTree
from pydub import AudioSegment

# TODO: Loading bar
# TODO: File name with pseudonymn

class Eaf:
    """Store information about annotation tiers from EAF files"""
    def __init__(self, path):
        self.path = path
        self.time_order = {}
        self.tiers = {}
        self.annotations = {}
        self.overlapped = {}
        self.not_overlapped = {}
        self.no_gaps = {}
        self.no_smalls = {}

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
        for key in self.tiers.keys():
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

    def show_tiers(self):
        """Display tiers' name"""
        for key in self.tiers.keys():
            print(key)

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
        selected_tiers = []
        temp = {}
        intervals = {}

        # Store in a list the name of the tiers selected by the user
        for tier in self.tiers.keys():
            if tier not in exceptions:
                selected_tiers.append(tier)
            else:
                continue

        # Store in a dict the pair with begin and end time (in milliseconds) of each selected tier
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
        reference_tier = list(self.not_overlapped.values())
        annotation_id = list(self.not_overlapped.keys())
        other_tiers_begins = list()
        begin = 0
        end = 1
        duration = 2

        def normal_values():
            self.no_gaps[annotation_id[index]] = reference_tier[index]

        def modified_values():
            self.no_gaps[annotation_id[index]] = reference_tier[index]
            self.no_gaps[annotation_id[index]][end] = reference_tier[index+1][begin]
            self.no_gaps[annotation_id[index]][duration] = reference_tier[index+1][begin] - reference_tier[index][begin]

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
                    if obstacle:
                        # If there is an annotation in between
                        normal_values()
                    else:
                        # If there is not
                        modified_values()
            else:
                # If the annotation has more than 2 seconds, check if the gap between the annotation
                # and the next is larger than 1 second and a half
                if reference_tier[index+1][begin] - reference_tier[index][end] > 1500:
                    normal_values()
                else:
                    obstacle = False
                    for time_value in other_tiers_begins:
                        if reference_tier[index][end] <= time_value <= reference_tier[index+1][begin]:
                            obstacle = True
                        else:
                            continue
                    if obstacle:
                        normal_values()
                    else:
                        modified_values()

    def remove_small_clusters(self):
        reference_tier = list(self.no_gaps.values())
        annotation_id = list(self.no_gaps.keys())
        begin = 0
        end = 1
        duration = 2
        mod1 = 0
        mod2 = 1
        contiguous = False
        large_enough = False

        for index in range(len(reference_tier) - 4):
            while reference_tier[index+mod1][end] == reference_tier[index+mod2][begin]:
                contiguous = True
                if reference_tier[index+mod2][end] - reference_tier[index][begin] >= 2000:
                    large_enough = True
                    break
                else:
                    mod1 += 1
                    mod2 += 1
            if not contiguous:
                if reference_tier[index][duration] >= 2000:
                    continue
                elif reference_tier[index][begin] == reference_tier[index-1][end]:
                    continue
                else:
                    del reference_tier[index]
                    del annotation_id[index]
            if not large_enough:
                if reference_tier[index][begin] == reference_tier[index-1][end]:
                    continue
                else:
                    del reference_tier[index]
                    del annotation_id[index]

        for index in range(len(annotation_id)):
            self.no_smalls[annotation_id[index]] = reference_tier[index]

    def write_eaf(self, ref_tier_id):
        reference_tier = []
        annotation_id = []
        all_annotations_id = []
        new_tier_id = ref_tier_id + " Modified"

        for values in self.no_smalls.values():
            reference_tier.append(values[:])

        for tier in self.tiers.values():
            for annotation in tier.keys():
                all_annotations_id.append(int(annotation[1:]))

        highest_id = max(all_annotations_id)

        add = 1
        for index in range(len(reference_tier)):
            annotation_id.append("a" + str(highest_id + add))
            add += 1

        for index in range(len(reference_tier)):
            for key, value in self.time_order.items():
                if reference_tier[index][0] == int(value):
                    reference_tier[index][0] = key
                elif reference_tier[index][1] == int(value):
                    reference_tier[index][1] = key
                else:
                    continue

        ElementTree.SubElement(self.root, 'TIER',
                               attrib={
                                   'LINGUISTIC_TYPE_REF': 'default-lt',
                                   'TIER_ID': new_tier_id})

        for index in range(len(reference_tier)):
            ElementTree.SubElement(self.root.findall('TIER')[-1], 'ANNOTATION')
            ElementTree.SubElement(
                self.root.findall('TIER')[-1].findall('ANNOTATION')[-1],
                'ALIGNABLE_ANNOTATION',
                attrib={
                    'ANNOTATION_ID': annotation_id[index],
                    'TIME_SLOT_REF1': reference_tier[index][0],
                    'TIME_SLOT_REF2': reference_tier[index][1]
                    }
            )
            ElementTree.SubElement(
                 self.root.findall('TIER')[-1].findall('ANNOTATION')[-1].find('ALIGNABLE_ANNOTATION'),
                 'ANNOTATION_VALUE'
            )
            self.root.findall('TIER')[-1].findall('ANNOTATION')[-1].find('ALIGNABLE_ANNOTATION').find('ANNOTATION_VALUE').text = reference_tier[index][3]

        def indent(elem, level=0):
            i = "\n" + level * "  "
            j = "\n" + (level - 1) * "  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for subelem in elem:
                    indent(subelem, level + 1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = j
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = j
            return elem

        indent(self.root)
        self.tree.write('output2.xml', encoding="utf-8")

    def extract_audio(self, audio_path):
        audio = AudioSegment.from_wav(audio_path)
        os.mkdir(path='output')
        for key, value in self.no_smalls.items():
            audio_cut = audio[value[0]:value[1]]
            filename = str(key) + "_" + str(value[0]) + "_" + str(value[1]) + "_" + str(value[2]) + ".wav"
            audio_cut.export('output/' + filename, format='wav')

        for key, value in self.no_smalls.items():
            filename = str(key) + "_" + str(value[0]) + "_" + str(value[1]) + "_" + str(value[2]) + ".txt"
            file_created = open('output/' + filename, "w")
            file_created.write(value[3])
            file_created.close()

# Test area --------------------------------------


test = Eaf(path='Sample_Files/RicardoR.xml')
test.remove_overlaps('S1', ['Dados Contextuais', 'Roteiro'])
test.remove_gaps('S1')
test.remove_small_clusters()
test.write_eaf(ref_tier_id='S1')
test.extract_audio(
    audio_path='/home/gustavo/Drive_New/Universidade/Producao/Mestrado/Scripts/Python/Sample_Files/RicardoR.wav')

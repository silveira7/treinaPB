from datetime import datetime
import xml.etree.ElementTree as ElementTree
import json
import sys
from pathlib import Path
from pydub import AudioSegment
import pretty_xml


class Eaf:
    """Store information about annotation tiers from EAF files"""

    def __init__(self, path, reference_tier):
        self.path = Path(path)
        self.reference_tier = reference_tier
        self.tree = ElementTree.parse(path)
        self.xml = self.tree.getroot()
        self.tiers = self.parse()
        self.groups = {}

    def timetable(self):
        """Extract time-related information from EAF and store it in a dictionary.

        timetable = {time_slot_id: time_value}
        """
        timetable = {}
        for child in self.xml.find("TIME_ORDER"):
            timetable[child.attrib.get("TIME_SLOT_ID")] = child.attrib.get("TIME_VALUE")
        return timetable

    def parse(self):
        """Extract the information from EAF and store it in a dictionary.

        tiers = {annotation ID: {begin_time_slot: ..., end_time_slot: ..., annotation_value: ...,
        begin_time_value: ..., end_time_value: ..., begin_time_value_formatted: ..., end_time_value_formatted: ...}}
        """
        annotations = {}
        tiers = {}

        # For each tier...
        for child in self.xml.findall("TIER"):
            #  Loop each annotation of the tier
            for sub_child in child.findall("ANNOTATION"):
                annotations[sub_child[0].attrib.get("ANNOTATION_ID")] = {
                    "begin_time_slot": sub_child[0].attrib.get("TIME_SLOT_REF1"),
                    "end_time_slot": sub_child[0].attrib.get("TIME_SLOT_REF2"),
                    "annotation_value": sub_child[0][0].text,
                }
            tiers[child.attrib.get("TIER_ID")] = annotations
            annotations = {}

        # From time slot IDs, get the time of each annotation's boundaries
        timetable = self.timetable()
        for key in tiers:
            # Loop each annotation of the tier
            for sub_key in tiers[key].keys():
                # Store begin_time_value in milliseconds
                tiers[key][sub_key]["begin_time_value"] = int(
                    timetable[tiers[key][sub_key]["begin_time_slot"]]
                )

                # Store end_time_value in milliseconds
                tiers[key][sub_key]["end_time_value"] = int(
                    timetable[tiers[key][sub_key]["end_time_slot"]]
                )

                # Store duration in milliseconds
                tiers[key][sub_key]["duration"] = int(
                    tiers[key][sub_key]["end_time_value"]
                ) - int(tiers[key][sub_key]["begin_time_value"])

                # Store begin_time_value_formatted in H:M:S.f format
                tiers[key][sub_key][
                    "begin_time_value_formatted"
                ] = datetime.utcfromtimestamp(
                    tiers[key][sub_key]["begin_time_value"] / 1000
                ).strftime(
                    "%H:%M:%S.%f"
                )

                # Store end_time_value_formatted in H:M:S.f format
                tiers[key][sub_key][
                    "end_time_value_formatted"
                ] = datetime.utcfromtimestamp(
                    tiers[key][sub_key]["end_time_value"] / 1000
                ).strftime(
                    "%H:%M:%S.%f"
                )
        return tiers

    def view_tier(self, tier):
        """Organized display of information of all annotations of a tier."""
        for annotation in self.tiers[tier]:
            print(
                "Annotation ID: "
                + annotation
                + "\n"
                + "Begin: "
                + self.tiers[tier][annotation]["begin_time_value_formatted"]
                + f" ({self.tiers[tier][annotation]['begin_time_value']} ms)"
                + "\n"
                + "End: "
                + self.tiers[tier][annotation]["end_time_value_formatted"]
                + f" ({self.tiers[tier][annotation]['end_time_value']} ms)"
                + "\n"
                + "Duration: "
                + f"{str(self.tiers[tier][annotation]['duration'])} ms"
                + "\n"
                + "Content: "
                + '"'
                + self.tiers[tier][annotation]["annotation_value"]
                + '"'
                + "\n"
            )

    def export_json(self):
        """Export tiers to JSON file."""
        with open(self.path.with_suffix(".json"), "w") as opened_file:
            opened_file.write(
                json.dumps(self.tiers, indent=4, ensure_ascii=False)
            )

    def remove_overlapped(self, exceptions):
        """Get all annotations of a tier that do not overlap with annotations of other tiers"""

        selected_tiers = []  # To store the selected tier from reference_tier and exceptions
        temp = {}  # Transitory variable to build the intervals dic
        intervals = {}  # {each tier: {begin: end, begin: end, ...}}

        if exceptions is None:
            exceptions = []

        for exception in exceptions:
            if exception not in self.tiers.keys():
                print(f"=> {exception}")
                raise NameError(f"name {exception} is not defined")

        # Store in a list the name of the tiers selected by the user
        for tier in self.tiers:
            if tier not in exceptions:
                selected_tiers.append(tier)
            else:
                continue

        # Store in a dic the pair with begin and end time (in milliseconds) of each
        # annotation of each selected tier
        for tier in selected_tiers:
            for attrib in self.tiers[tier].values():
                temp[attrib["begin_time_value"]] = attrib["end_time_value"]
            intervals[tier] = temp
            temp = {}

        overlapped = {}
        # Check if intervals of reference tier overlap with intervals of other tiers
        # Loop through intervals of reference tier
        for ref_tier_interval_begin, ref_tier_interval_end in intervals[
            self.reference_tier
        ].items():
            # Restrict to selected tiers that are not the reference tier
            for other_tier in selected_tiers:
                out = False  # Boolean variable used to get out of nested loops
                if other_tier != self.reference_tier:
                    for other_tier_interval_begin, other_tier_interval_end in intervals[
                        other_tier
                    ].items():
                        # Check if the interval of reference tier overlaps with at
                        # least one interval of another tier
                        if (
                            ref_tier_interval_begin <= other_tier_interval_end
                            and other_tier_interval_begin <= ref_tier_interval_end
                        ):
                            # If so, store the interval and get out of the loop
                            overlapped[ref_tier_interval_begin] = ref_tier_interval_end
                            out = True
                            break  # Go out of the inner loop
                else:
                    continue
                if out:
                    break  # Go out of the outer loop

        # From overlapped intervals, get a dic with information of not overlapped annotations
        for annotation, attrib in self.tiers[self.reference_tier].copy().items():
            # Check if interval is not overlapped
            if (attrib["begin_time_value"] in overlapped.keys()) and (
                attrib["end_time_value"] in overlapped.values()
            ):
                self.tiers[self.reference_tier].pop(annotation)
            else:
                continue

    def remove_gaps(self):
        """Remove gaps between annotations that form a cluster"""

        # TODO Atualizar tempo formatado

        timetable = self.timetable()
        # Store list of attributes of not overlapped annotations
        reference_tier = list(self.tiers[self.reference_tier].values())

        # Store list of IDs of not overlapped annotations
        annotation_id = list(self.tiers[self.reference_tier].keys())
        # To store the begin time of all annotations of the others tiers (not ref tier)
        other_tiers_begins = list()

        def normal_values():
            """Store in no_gaps the regular begin, end and duration of the annotation"""
            # TODO Maybe this function is unnecessary
            self.tiers[self.reference_tier][annotation_id[index]] = reference_tier[index]

        def modified_values():
            """Store in no_gaps the regular begin, but modified end
            and duration of the annotation"""

            # The end of the current annotation is set to be the same
            # as the beginning of the next annotation
            modified_duration = (
                reference_tier[index + 1]["begin_time_value"]
                - reference_tier[index]["begin_time_value"]
            )
            self.tiers[self.reference_tier][annotation_id[index]][
                "end_time_value"
            ] = reference_tier[index + 1]["begin_time_value"]
            self.tiers[self.reference_tier][annotation_id[index]]["duration"] = modified_duration
            time_key = list(timetable.values()).index(
                str(reference_tier[index + 1]["begin_time_value"])
            )
            self.tiers[self.reference_tier][annotation_id[index]]["end_time_slot"] = list(
                timetable.keys()
            )[time_key]

        # Create a list with the begin time value of all intervals of other tiers
        for tier, annotation in self.tiers.items():
            if tier != self.reference_tier:
                for attrib in annotation.values():
                    if attrib["begin_time_value"] not in other_tiers_begins:
                        other_tiers_begins.append(attrib["begin_time_value"])
                    else:
                        continue
            else:
                continue

        # Loop to remove time gaps inside clusters of annotations
        for index in range(len(reference_tier) - 1):
            # Check if the annotation has 2 seconds or less
            if reference_tier[index]["duration"] <= 2000:
                # Check if the gap between the current annotation
                # and the next is larger than 1,5 second
                if (
                    reference_tier[index + 1]["begin_time_value"]
                    - reference_tier[index]["end_time_value"]
                    > 1500
                ):
                    # Check if the gap between the current annotation and
                    # the previous one is larger than 1,5 second
                    if (
                        reference_tier[index]["begin_time_value"]
                        - reference_tier[index - 1]["end_time_value"]
                        > 1500
                    ):
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
                        if (
                            reference_tier[index]["end_time_value"]
                            <= time_value
                            <= reference_tier[index + 1]["begin_time_value"]
                        ):
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
                if (
                    reference_tier[index + 1]["begin_time_value"]
                    - reference_tier[index]["end_time_value"]
                    > 1500
                ):
                    normal_values()
                else:
                    # If the gap between the current annotation and the next is less than 1,5 second
                    # Check if there is an annotation in between
                    obstacle = False
                    for time_value in other_tiers_begins:
                        if (
                            reference_tier[index]["end_time_value"]
                            <= time_value
                            <= reference_tier[index + 1]["begin_time_value"]
                        ):
                            obstacle = True
                        else:
                            continue
                    # If there is an annotation in between
                    if obstacle:
                        normal_values()
                    # If there is not
                    else:
                        modified_values()

    def write_eaf(self):
        """Write a new EAF/XML file with the original tiers and a new tier comprising the annotations
        filtered by the functions remove_overlaps, remove_gaps and remove_small_clusters.
        """

        # Add a new TIER element in XML tree and attributes
        tier_id = self.reference_tier + " Modified"
        ElementTree.SubElement(
            self.xml,
            "TIER",
            attrib={"LINGUISTIC_TYPE_REF": "default-lt", "TIER_ID": tier_id},
        )

        # Add inner elements to the just created TIER element
        for annotation_id, parameters in self.tiers[self.reference_tier].items():
            # Add ANNOTATION elements
            ElementTree.SubElement(self.xml.findall("TIER")[-1], "ANNOTATION")
            # Add ALIGNABLE_ANNOTATION elements and attributes
            ElementTree.SubElement(
                self.xml.findall("TIER")[-1].findall("ANNOTATION")[-1],
                "ALIGNABLE_ANNOTATION",
                attrib={
                    "ANNOTATION_ID": annotation_id,
                    "TIME_SLOT_REF1": parameters["begin_time_slot"],
                    "TIME_SLOT_REF2": parameters["end_time_slot"],
                },
            )
            # Add ANNOTATION_VALUE elements
            ElementTree.SubElement(
                self.xml.findall("TIER")[-1]
                .findall("ANNOTATION")[-1]
                .find("ALIGNABLE_ANNOTATION"),
                "ANNOTATION_VALUE",
            )
            # Add text to ANNOTATION_VALUE elements
            self.xml.findall("TIER")[-1].findall("ANNOTATION")[-1].find(
                "ALIGNABLE_ANNOTATION"
            ).find("ANNOTATION_VALUE").text = parameters["annotation_value"]

        # Fix the format of the new XML/EAF code
        pretty_xml.indent(self.xml)

        # Create directory for eaf files
        eaf_folder = self.path.parent / "modified_eaf"
        eaf_folder.mkdir(exist_ok=True)

        # Write the new XML/EAF file using UTF-8 encoding
        new_eaf_name = self.path.stem + "_HTK.eaf"
        new_eaf_path = eaf_folder / new_eaf_name
        self.tree.write(new_eaf_path, encoding="utf-8")

    def group(self):
        """Create groups of annotations with duration ranging between four and eight seconds"""

        # Variables created only to make the following loop more readable
        group_num = 1
        counter = 0

        keys_list = list(self.tiers[self.reference_tier].keys())

        for key, value in self.tiers[self.reference_tier].items():
            # If annotation is the first of the list
            if key == keys_list[0]:
                # Store the next annotation parameters
                next_annotation = self.tiers[self.reference_tier][keys_list[1]]["begin_time_value"]
                # If current annotation's end matches next annotation's begin
                if value["end_time_value"] == next_annotation:
                    # Insert group_num in the 2nd position
                    value["group"] = group_num
                # Else, insert the value 'Isolated' and do not update group_num
                # since it was not used for current annotation
                else:
                    value["group"] = "Isolated"
            # If annotation is the last of the list
            elif key == keys_list[-1]:
                # Store the previous annotation parameters
                previous_annotation = self.tiers[self.reference_tier][keys_list[-2]]["end_time_value"]
                # If current annotation's begin matches previous annotation's end
                if value["begin_time_value"] == previous_annotation:
                    # Insert group_num in 2nd position
                    value["group"] = group_num
                # Else, insert the value 'Isolated' and do not update group_num
                else:
                    value["group"] = "Isolated"
            # If annotation is not the first nor the last
            else:
                # Stores the previous annotation's parameters
                previous_annotation = self.tiers[self.reference_tier][keys_list[counter - 1]][
                    "end_time_value"
                ]
                # Stores the next annotation's parameters
                next_annotation = self.tiers[self.reference_tier][keys_list[counter + 1]][
                    "begin_time_value"
                ]
                # If current annotation's end matches next annotation's begin
                if value["end_time_value"] == next_annotation:
                    # Insert group_num in 2nd position
                    value["group"] = group_num
                # Otherwise, if current annotation's begin matches previous annotation's end
                elif value["begin_time_value"] == previous_annotation:
                    # Insert group_num in 2nd position
                    value["group"] = group_num
                    # Update group_num since the annotation is the last of the current group
                    group_num += 1
                # Else, insert 'Isolated' and do not update group_num
                else:
                    value["group"] = "Isolated"
            counter += 1

    def get_groups(self):
        """Create dic that stores information about groups of annotations"""
        ids = set()  # Stores group IDs
        groups = {}

        # Create a set of all group IDs
        for value in self.tiers[self.reference_tier].values():
            ids.add(value["group"])

        # Create the structure of groups dic: {id_number: [ duration, [annotations' IDs] ]}
        for id_number in ids:
            groups[id_number] = [0, []]

        # Stores group information in groups dic
        for annotation_id, parameters in self.tiers[self.reference_tier].items():
            for group_id, group_parameters in groups.items():
                if parameters["group"] == group_id:
                    group_parameters[0] += parameters["duration"]
                    group_parameters[1].append(annotation_id)

        return groups

    def split(self):
        """Iterates split function until there is no more big groups"""

        def _split(local_groups, local_big_groups, local_tier):
            split = False  # Boolean variable to check if annotation was split or not
            annotations = list()  # Temp. variable to store the annotations' ID of th
            new_group_duration = None

            # Loop to split big groups
            for each_big_group in local_big_groups:
                # For each big group, loop into all groups
                for group_id, parameters in local_groups.items():
                    # If current big group matches the group in groups dic
                    if each_big_group == group_id:
                        # Index to loop into annotations that are members of current big group
                        counter = 1
                        # Loop into current big group's annotations until
                        # the sum of their durations reach 8 seconds
                        # or until reach the last annotation
                        while (
                            counter < len(parameters[1])
                            and self.tiers[local_tier][parameters[1][counter]][
                                "end_time_value"
                            ]
                            - self.tiers[local_tier][parameters[1][0]]["begin_time_value"]
                            < 5000
                        ):
                            counter += 1
                        # If reach 8 seconds
                        if counter < len(parameters[1]):
                            # print(group_id, parameters[1])
                            # Set split as true, clear annotations list and
                            split = True
                            annotations = list()
                            # Store the joint duration of the remaining annotations (those that was
                            # no considered in previous while loop)
                            last_note_end = self.tiers[local_tier][
                                parameters[1][len(parameters[1]) - 1]
                            ]["end_time_value"]
                            current_note_begin = self.tiers[local_tier][
                                parameters[1][counter]
                            ]["begin_time_value"]
                            new_group_duration = last_note_end - current_note_begin
                            # Insert each remaining annotation into regrouped_annotations
                            while counter < len(parameters[1]):
                                annotations.append(parameters[1][counter])
                                counter += 1
                            # For each regrouped annotation
                            for annotation in annotations:
                                # Remove it from its original group
                                local_groups[group_id][1].remove(annotation)
                                # Update its group ID in grouped dic
                                self.tiers[local_tier][annotation]["group"] = len(local_groups) + 1
                            # Update the duration of the original group since it was split
                            local_groups[group_id][0] = (
                                    local_groups[group_id][0] - new_group_duration
                            )
                        else:
                            continue
                    else:
                        continue
                # If current group was split, insert the group's information in groups dic
                if split:
                    local_groups[len(local_groups) + 1] = [
                        new_group_duration,
                        annotations,
                        each_big_group,
                    ]
                    split = False
            return local_groups

        big_groups = []
        groups = self.get_groups()

        while True:
            # Check if there is at least one group that lasts more than 12 seconds
            for key, value in groups.items():
                if key != "Isolated" and value[0] > 5000:
                    if (value[0] - 5000) > 4000:
                        if len(value[1]) > 1:
                            big_groups.append(key)
                else:
                    continue

            # If there isn't, stop the loop
            if not big_groups:
                break
            # Else (if there is), run split function
            else:
                groups = _split(groups, big_groups, self.reference_tier)
                big_groups = (
                    list()
                )  # Clear big_groups list before running the next loop

        modifier = 1

        last_group = None
        for index, key in enumerate(self.tiers[self.reference_tier].keys()):
            if index == 0:
                last_group = self.tiers[self.reference_tier][key]["group"]
                self.tiers[self.reference_tier][key]["group"] = modifier
            else:
                if self.tiers[self.reference_tier][key]["group"] == last_group:
                    self.tiers[self.reference_tier][key]["group"] = modifier
                else:
                    last_group = self.tiers[self.reference_tier][key]["group"]
                    modifier += 1
                    self.tiers[self.reference_tier][key]["group"] = modifier

    def extract_audio(self, one_channel=True, sample_rate=16000, codec='pcm_s16le'):
        """Extract and write the WAV file for each annotation and
        a TXT file with the annotation's content"""

        audio_source = self.path.with_suffix(".wav")

        # Import WAV file
        audio = AudioSegment.from_wav(audio_source)

        if one_channel:
            audio = audio.set_channels(1)

        if sample_rate:
            audio = audio.set_frame_rate(sample_rate)

        groups = self.get_groups()

        # Create subdir in output for each audio source
        chunks_directory = audio_source.parent / "chunks"
        chunks_directory.mkdir(exist_ok=True)

        for group_id, parameters in groups.items():
            begin = self.tiers[self.reference_tier][parameters[1][0]]["begin_time_value"]
            end = self.tiers[self.reference_tier][parameters[1][-1]]["end_time_value"]
            totaldur = end - begin

            if 3000 < totaldur < 7000:
                audio_cut = audio[begin:end]
                filename = (
                    audio_source.stem
                    + "_"
                    + str(group_id).zfill(3)
                    + "_"
                    + str(begin)
                    + "_"
                    + str(end)
                )
                filepath = chunks_directory / filename
                text = ""

                for annotation_id in parameters[1]:
                    text += " " + self.tiers[self.reference_tier][annotation_id]["annotation_value"]

                audio_cut.export(filepath.with_suffix(".wav"), format="wav", codec=codec)

                with open(filepath.with_suffix(".lab"), "w") as opened_file:
                    opened_file.write(text)


if __name__ == "__main__":
    DIRECTORY = Path(sys.argv[1])
    REFERENCE_TIER = sys.argv[2]
    EXCEPTIONS = sys.argv[3:]

    eaf_files = list(DIRECTORY.glob('*.eaf'))
    for file in eaf_files:
        print(file)
        my_eaf = Eaf(file, REFERENCE_TIER)
        my_eaf.export_json()
        my_eaf.remove_overlapped(EXCEPTIONS)
        my_eaf.remove_gaps()
        my_eaf.write_eaf()
        my_eaf.group()
        my_eaf.split()
        my_eaf.extract_audio()
    print("Finished.")

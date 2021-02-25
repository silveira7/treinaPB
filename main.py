import os
import sys
import re
from eaf import Eaf


try:
    if os.path.exists(sys.argv[1]):
        directory = sys.argv[1]
        os.chdir(directory)
    else:
        print('Error: The specified directory does not exist.')
        sys.exit(1)
except IndexError:
    print('Error: No directory was specified.')
    sys.exit(1)

files = os.listdir(directory)

eaf_files = list()

for file in files:
    match = re.search(r'.*\.eaf', file)
    if match:
        eaf_files.append(match.group())
    else:
        continue

if not eaf_files:
    print('Error: There is not any EAF file in the specified directory.')
    sys.exit(1)

try:
    reference_tier = sys.argv[2]
except IndexError:
    print("Error: No reference tier was specified.")
    sys.exit(1)

try:
    exceptions = sys.argv[3:]
except IndexError:
    print("Error: No exception tier(s) was specified.")
    sys.exit(1)

file_number = 0
number_of_groups = {}

print('EAF Editor is running:')

for file in eaf_files:
    file_number += 1
    file_index = 'File ' + str(file_number) + ' - '

    print('\t' + file_index + 'Reading ' + file + '...')
    filename = Eaf(path=file)

    try:
        print('\t' + file_index + 'Removing overlapped annotations in ' + reference_tier + ' tier...')
        filename.remove_overlaps(reference_tier, exceptions)
    except KeyError:
        print('Error: The specified tiers could not be found in ' + file)
        sys.exit(1)

    print('\t' + file_index + 'Removing gaps inside clusters of annotations...')
    filename.remove_gaps(reference_tier)

    print('\t' + file_index + 'Removing small annotations...')
    filename.remove_small_clusters()

    print('\t' + file_index + 'Writing new EAF file...')
    filename.write_eaf(ref_tier_id='S1')

    print('\t' + file_index + 'Grouping annotations...')
    filename.split_iter()
    group_list = []
    for key, value in filename.groups.items():
        group_list.append(str(key) + " " + str(value[0]) + "\n")
    number_of_groups[file] = [filename.get_number_of_groups(), group_list]

    print('\t' + file_index + 'Exporting media file...')

    try:
        filename.extract_audio(audio_source=os.path.join(os.getcwd(), file[:-3] + 'wav'))
    except FileNotFoundError:
        print("Error: Cannot find " + os.path.join(os.getcwd(), file[:-3] + 'wav'))


number_of_groups_list = list()

for key, value in number_of_groups.items():
    number_of_groups_list.append(str(key) + "\t " + str(value[0]) + " groups\n")
    for duration in number_of_groups[key][1]:
        number_of_groups_list.append("\t" + str(duration))


number_of_groups_list = "".join(number_of_groups_list)

newfile = open(sys.argv[1] + "number_of_groups.txt", "w")
newfile.write(number_of_groups_list)
newfile.close()

print("Process successfully concluded.")

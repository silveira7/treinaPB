import os
import sys
import re
from eaf import Eaf


try:
    if os.path.exists(sys.argv[1]):
        directory = sys.argv[1]
        os.chdir(directory)
    else:
        print('Error: The specified directory does not exists.')
        sys.exit(1)
except IndexError:
    print('Error: No directory was specified.')
    sys.exit(1)

files = os.listdir(directory)

for file in files:
    match = re.search('.*\\.eaf', file)
    if match:
        try:
            eaf_files.append(match.group())
        except NameError:
            eaf_files = [match.group()]
    else:
        continue

try:
    eaf_files
except NameError:
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

    print('\t' + file_index + 'Exporting media file...')
    filename.extract_audio(audio_source=os.path.join(os.getcwd(), file[:-3] + 'wav'))

print("Process successfully concluded.")

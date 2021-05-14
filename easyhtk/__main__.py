import sys
from pathlib import Path
import time
from eaf import Eaf


start_time = time.time()

try:
    if Path(sys.argv[1]).exists():
        DIRECTORY = Path(sys.argv[1])
    else:
        print('Error 1: The specified directory does not exist.')
        sys.exit(1)
except IndexError:
    print('Error 2: No directory was specified.')
    sys.exit(1)

eaf_files = list(DIRECTORY.glob('*.eaf'))

if not eaf_files:
    print('Error 3: There is not any EAF file in the specified directory.')
    sys.exit(1)

try:
    REFERENCE_TIER = sys.argv[2]
except IndexError:
    print("Error 4: No reference tier was specified.")
    sys.exit(1)

EXCEPTIONS = sys.argv[3:]

if not EXCEPTIONS:
    answer = ""
    while answer not in ["yes", "no"]:
        answer = input("No exception tier was specified. Do you want to continue? (yes or no): ")
        if answer == "yes":
            break
        elif answer == "no":
            print("Program finished.")
            sys.exit(1)

number_of_groups = {}

for file in eaf_files:
    print(file.name + ' - Reading...')
    eaf = Eaf(file)

    try:
        print(file.name + ' - Removing overlapped annotations in ' + REFERENCE_TIER + ' tier...')
        eaf.remove_overlaps(REFERENCE_TIER, EXCEPTIONS)
    except NameError:
        print(f'Error 5: Exception tier(s) could not be found in ' + file.name)
        sys.exit(1)

    print(file.name + ' - Removing gaps inside clusters of annotations...')
    eaf.remove_gaps(REFERENCE_TIER)

    print(file.name + ' - Removing small annotations...')
    eaf.remove_small_clusters()

    print(file.name + ' - Writing new EAF file...')
    eaf.write_eaf(REFERENCE_TIER)

    print(file.name + ' - Grouping annotations...')
    eaf.split_iter()

    print(file.name + ' - Exporting media file...')
    wav_file = file.with_suffix('.wav')
    try:
        pass
        eaf.extract_audio(wav_file)
    except FileNotFoundError:
        print("Error 6: Cannot find " + wav_file.name)

print("\neasyHTK finished.")
print("Time running: %s seconds." % (time.time() - start_time))

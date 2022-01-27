"""
TreinaPB: Training HTK models for forced alignment in Brazilian Portuguese.
"""

__version__ = '0.1'
__author__ = 'Gustavo Silveira'

import sys
import os
import re
import subprocess
import pathlib
import argparse
import json

import eaf
import clean
import checker
import dictionary
import textgrid
import audio


parser = argparse.ArgumentParser(
    prog='TreinaPB',
    description='Training HTK models for forced alignment in Brazilian Portuguese.')

required_args = parser.add_argument_group('required arguments')

required_args.add_argument(
    '-d', '--directory',
    type=pathlib.Path,
    help='path to the directory with recording (.wav) and trascription files (.eaf).')

required_args.add_argument(
    '-r','--reference',
    type=str,
    help='name of the reference tier in the transcription files.')

required_args.add_argument(
    '-i', '--ignore',
    type=str,
    help='names of the tiers to ignore when checking for overlaps.',
    nargs='*')

args = parser.parse_args()

SRC = pathlib.Path(__file__).parent
BASE = SRC.parent
MESSAGES = SRC / "messages.json"
VAR = BASE / "var"
HTK_CONFIG = VAR / "por.yaml"
HTK_DIC = VAR / "dic.txt"
HTK_MODEL = VAR / "model.zip"
HTK_HDMAN = BASE / "htk" / "HTKTools" / "HDMan"
PRAAT = BASE / "praat" / "praat"
PRAAT_SCRIPTS = SRC / "praat"
PRAAT_TABLEOFREAL = SRC / "praat" / "BP.TableOfReal"

with open(SRC / "messages.json") as opened_file:
    messages = opened_file.read()

messages = json.loads(messages)

os.chdir(BASE)

# Check if DIRECTORY was specified and exists
if args.directory is None:
    print(messages['errors']['1'])
    sys.exit(1)
elif args.directory.exists():
    DIRECTORY = args.directory
    CHUNKS_DIR = DIRECTORY / "chunks"
else:
    print(messages['errors']['2'])
    sys.exit(1)

# Try to find EAF files
eaf_files = tuple(DIRECTORY.glob('*.eaf'))
if not eaf_files:
    print(messages['errors']['3'])
    sys.exit(1)

# Check if REFERENCE was specified
if args.reference is None:
    print(messages['errors']['4'])
    sys.exit(1)
else:
    REFERENCE_TIER = args.reference


def check_ignore():
    if args.ignore is None or args.ignore == []:
        answer = ""
        first = True
        while answer not in ["yes", "no"]:
            if first:
                first = False
                answer = input(messages['interactions']['check_ignore'][0])
            else:
                answer = input(messages['interactions']['check_ignore'][1])
            if answer == "no":
                print("Exiting.")
                sys.exit(1)
            elif answer == "yes":
                break

check_ignore()
IGNORE = args.ignore

for file in eaf_files:
    print(file.stem + ' - Reading files...')
    eaf = eaf.Eaf(file, REFERENCE_TIER)

    print(file.stem
          + ' - Removing overlapped annotations in '
          + REFERENCE_TIER
          + ' tier...')

    eaf.remove_overlapped(IGNORE)

    print(file.stem + ' - Removing gaps between annotations...')
    eaf.remove_gaps()

    print(file.stem + ' - Writing new EAF file...')
    eaf.write_eaf()

    print(file.stem + ' - Grouping annotations...')
    eaf.group()
    eaf.split()

    print(file.stem + ' - Exporting media files...\n')
    wav_file = file.with_suffix('.wav')
    eaf.extract_audio(wav_file)

clean.empties(CHUNKS_DIR)
clean.broken_audios(CHUNKS_DIR)
clean.multiline(CHUNKS_DIR)
clean.punctwhite(CHUNKS_DIR)
clean.nonwords(CHUNKS_DIR, VAR)
clean.isoletter(CHUNKS_DIR)
clean.smalliso(CHUNKS_DIR)
clean.remove_empties(CHUNKS_DIR)
checker.early_check(CHUNKS_DIR, VAR)

dictionary.gendict(CHUNKS_DIR, HTK_DIC)
dictionary.fixdict(HTK_DIC)

subprocess.call(
    ['python3',
     '-m', "aligner",
     '-c', HTK_CONFIG,
     '-d', HTK_DIC,
     '-e', '10',
     '-t', CHUNKS_DIR,
     '-w', HTK_MODEL]
)

subprocess.call(
    ['python3',
     '-m', "aligner",
     '-r', HTK_MODEL,
     '-d', HTK_DIC,
     '-a', CHUNKS_DIR]
)

textgrid.fix_encoding(CHUNKS_DIR)

tg = textgrid.TextGrid(str(CHUNKS_DIR))
tg.get_metadata()
tg.build_tg()

textgrid.create_vv_tier(CHUNKS_DIR)
audio.retrieve(CHUNKS_DIR)
checker.late_check(CHUNKS_DIR)
clean.final_clean(CHUNKS_DIR)

subprocess.call(
    [PRAAT, '--run',
     str(PRAAT_SCRIPTS / "merge_wav_tg.praat"),
     str(CHUNKS_DIR) + "/"]
)

for file in CHUNKS_DIR.iterdir():
    if re.search(r".*merged.*", file.name):
        file.unlink(missing_ok=True)

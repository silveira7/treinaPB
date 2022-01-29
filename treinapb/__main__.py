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

import treinapb.eaf
import treinapb.clean
import treinapb.checker
import treinapb.dictionary
import treinapb.textgrid
import treinapb.audio

SRC = pathlib.Path(__file__).parent
BASE = SRC.parent
MESSAGES = SRC / "messages.json"
VAR = BASE / "var"
HTK_CONFIG = VAR / "por.yaml"
HTK_DICT = VAR / "dic.txt"
HTK_MODEL = VAR / "model.zip"

if sys.platform == "linux":
    PRAAT = BASE / "praat" / "praat-linux"
elif sys.platform == "darwin":
    PRAAT = BASE / "praat" / "praat-mac"
elif sys.platform == "win32":
    PRAAT = BASE / "praat" / "praat-win.exe"

PRAAT_SCRIPTS = SRC / "praat"
PRAAT_TABLEOFREAL = SRC / "praat" / "BP.TableOfReal"
DIRECTORY = None
REFERENCE_TIER = None
IGNORE = None
CHUNKS_DIR = None

parser = argparse.ArgumentParser(
    prog='TreinaPB',
    description='Training HTK models for forced alignment in Brazilian Portuguese.')

required_args = parser.add_argument_group('required arguments')

required_args.add_argument(
    '-d', '--directory',
    type=pathlib.Path,
    help='path to the directory with recording (.wav) and trascription files (.eaf).')

required_args.add_argument(
    '-r', '--reference',
    type=str,
    help='name of the reference tier in the transcription files.')

required_args.add_argument(
    '-i', '--ignore',
    type=str,
    help='names of the tiers to ignore when checking for overlaps.',
    nargs='*')

args = parser.parse_args()

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

# Check if REFERENCE was specified
if args.reference is None:
    print(messages['errors']['4'])
    sys.exit(1)
else:
    REFERENCE_TIER = args.reference


def check_ignore(ignore, msg):
    if ignore is None or ignore == []:
        answer = ""
        first = True
        while answer not in ["yes", "no"]:
            if first:
                first = False
                answer = input(msg['interactions']['check_ignore'][0])
            else:
                answer = input(msg['interactions']['check_ignore'][1])
            if answer == "no":
                print("Exiting.")
                sys.exit(1)
            elif answer == "yes":
                break


check_ignore(args.ignore, messages)
IGNORE = args.ignore


def run_eaf(directory, reference_tier, ignore, msg):
    # Try to find EAF files
    eaf_files = tuple(directory.glob('*.eaf'))
    if not eaf_files:
        print(msg['errors']['3'])
        sys.exit(1)

    for file in eaf_files:
        print(file.stem + ' - Reading files...')
        eaf = treinapb.eaf.Eaf(file, reference_tier)

        print(file.stem
              + ' - Removing overlapped annotations in '
              + reference_tier
              + ' tier...')

        eaf.remove_overlapped(ignore)

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


def run_cleaner(chunks_dir, var):
    treinapb.clean.empties(chunks_dir)
    treinapb.clean.broken_audios(chunks_dir)
    treinapb.clean.multiline(chunks_dir)
    treinapb.clean.punctwhite(chunks_dir)
    treinapb.clean.nonwords(chunks_dir, var)
    treinapb.clean.isoletter(chunks_dir)
    treinapb.clean.smalliso(chunks_dir)
    treinapb.clean.remove_empties(chunks_dir)
    treinapb.checker.early_check(chunks_dir, var)


def run_dict(chunks_dir, htk_dict):
    treinapb.dictionary.gendict(chunks_dir, htk_dict)
    treinapb.dictionary.fixdict(htk_dict)


def run_htk(htk_config, htk_dic, chunks_dir, htk_model):
    subprocess.call(
        ['python3',
         '-m', "aligner",
         '-c', htk_config,
         '-d', htk_dic,
         '-e', '10',
         '-t', chunks_dir,
         '-w', htk_model]
    )

    subprocess.call(
        ['python3',
         '-m', "aligner",
         '-r', htk_model,
         '-d', htk_dic,
         '-a', chunks_dir]
    )


def run_praat(chunks_dir, praat_exe, praat_scripts):
    treinapb.textgrid.fix_encoding(chunks_dir)

    tg = treinapb.textgrid.TextGrid(str(chunks_dir))
    tg.get_metadata()
    tg.build_tg()

    treinapb.textgrid.create_vv_tier(chunks_dir)
    treinapb.audio.retrieve(chunks_dir)
    treinapb.checker.late_check(chunks_dir)
    treinapb.clean.final_clean(chunks_dir)

    subprocess.call(
        [praat_exe, '--run',
         str(praat_scripts / "merge_wav_tg.praat"),
         str(chunks_dir) + "/"]
    )

    for file in chunks_dir.iterdir():
        if re.search(r".*merged.*", file.name):
            file.unlink(missing_ok=True)


def main():
    run_eaf(DIRECTORY, REFERENCE_TIER, IGNORE, messages)
    run_cleaner(CHUNKS_DIR, VAR)
    run_dict(CHUNKS_DIR, HTK_DICT)
    run_htk(HTK_CONFIG, HTK_DICT, CHUNKS_DIR, HTK_MODEL)
    run_praat(CHUNKS_DIR, PRAAT, PRAAT_SCRIPTS)


if __name__ == '__main__':
    main()

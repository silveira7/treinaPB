# treinaPB

This project is under GNU General Public License v3.0.

# how to run?

Clone the repository, open a terminal emulator and run:

```
$ python3 run.py -d <directory> -r <reference tier> -i <tiers to ignore>
```

# help

```
usage: TreinaPB [-h] [-d DIRECTORY] [-r REFERENCE] [-i [IGNORE ...]]

Training HTK models for forced alignment in Brazilian Portuguese.

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -d DIRECTORY, --directory DIRECTORY
                        path to the directory with recording (.wav) and
                        trascription files (.eaf).
  -r REFERENCE, --reference REFERENCE
                        name of the reference tier in the transcription files.
  -i [IGNORE ...], --ignore [IGNORE ...]
                        names of the tiers to ignore when checking for
                        overlaps.
```

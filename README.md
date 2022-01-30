# treinaPB

This project is under GNU General Public License v3.0.

## Dependencies

The program was tested in a GNU/Linux operating system (Debian 11) using the following packages:

- Python 3.9
- ffmpeg 4.3.3
- Hidden Markov Model Toolkit (HTK) 3.4.1
- Praat 6.2.0.6

If you don't have [Python 3](https://www.python.org/downloads/) or [ffmpeg](https://ffmpeg.org/download.html), install it. In Debian-based GNU/Linux:
```
apt install python3 ffmpeg
```

The program depends on the following Python packages:
- pydub 0.25
- pyenchant 3.2.0
- sly 0.4
- nltk 3.6.7
- termcolor 1.1
- pandas 1.4
- numpy 1.12.0
- pyyaml 4.2b1
- scipy 0.18.1
- TextGrid 1.4

To automatically install these packages, go to the project's main folder and run in the console:

```
pip3 install -r requirements.txt
```

The program also depends on the `punkt` NLTK data. To install it directly in the command line, run:

```
python3 -m nltk.downloader punkt
```

Finally, a `pt_BR` (Brazilian Portuguese) dictionary also have to be installed in your computer. You can install it from one of these two providers: [hunspell](https://hunspell.github.io/) or [aspell](http://aspell.net/).

If you're running a Debian-based distribution of GNU/Linux, it should be available on the `apt` repositories:

```
sudo apt install hunspell-pt-br
```

## How to run?

1. Clone this repository
1. Install all the dependencies
1. Open a terminal emulator and run:

```
python3 run.py -d <directory> -r <reference tier> -i <tiers to ignore>
```

## Help

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

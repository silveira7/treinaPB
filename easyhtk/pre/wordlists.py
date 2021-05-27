#!/usr/bin/env python3

import re
from pathlib import Path
from collections import Counter


def _get_words(input_dir):
    print("Getting words...")
    labs = list(Path(input_dir).glob('*.lab'))
    lines = list()
    words = list()
    for lab in labs:
        with open(lab) as open_file:
            lines.append(open_file.readline())
    for line in lines:
        for word in line.split(sep=" "):
            words.append(word)
    return words


def _get_wordlists(words, output_dir):
    print("Creating wordlists...")
    normal_wordlist = []
    ou_wordlist = []
    r_wordlist = []

    words_count = sorted(Counter(words).items(),
                         key=lambda x: x[1], reverse=True)

    for pair in words_count:
        normal_wordlist.append(f"{str(pair[1]):<10} {pair[0]}\n")

    normal_wordlist = "".join(normal_wordlist)

    for word in words:
        if 'ou' in word:
            ou_wordlist.append(word)
        if re.search(r'r\b', word):
            r_wordlist.append(word)

    ou_wordlist = "\n".join(set(ou_wordlist))
    r_wordlist = "\n".join(set(r_wordlist))

    wordlists = [normal_wordlist, ou_wordlist, r_wordlist]
    counter = 0
    for filename in ["normal_wordlist.txt", "ou_wordlist.txt",
                     "r_wordlist.txt"]:
        path = Path(output_dir) / filename
        with open(path, "w") as open_file:
            open_file.write(wordlists[counter])
        counter += 1


def wordlists(input_dir, output_dir):
    words = _get_words(input_dir)
    _get_wordlists(words, output_dir)

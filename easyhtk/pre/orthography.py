#!/usr/bin/env python3

import re
from pathlib import Path


def _get_labs(input_dir):
    labs = list(Path(input_dir).glob('*.lab'))
    return labs


def _modify_ou(input_dir, exceptions_file):
    print("Modifying words with 'ou' dipthong...")
    labs = _get_labs(input_dir)

    with open(exceptions_file, 'r') as open_file:
        exceptions = open_file.readlines()

    # remove \n
    for index, word in enumerate(exceptions):
        exceptions[index] = word[:-1]

    def dashrepl(matchobj):
        onset = matchobj.groups()[0]
        ou = matchobj.groups()[1]
        end = matchobj.groups()[2]
        original_word = f"{onset}{ou}{end}"
        modified_word = f"{onset}o{end}"

        if original_word in exceptions:
            return original_word
        else:
            return modified_word

    for lab in labs:
        with open(lab, "r") as open_file:
            line = open_file.readline()
        s_pattern = re.compile(r"([a-z]*)(ou)([a-z]*)")
        if s_pattern.search(line):
            line = s_pattern.sub(dashrepl, line)
        with open(lab, "w") as open_file:
            open_file.write(line)


def _modify_r(input_dir, exceptions_file):
    print("Modifying words with final r...")
    labs = _get_labs(input_dir)

    with open(exceptions_file, 'r') as open_file:
        exceptions = open_file.readlines()

    for index, word in enumerate(exceptions):
        exceptions[index] = word[:-1]

    ehr = ['fizer', 'der', 'puder', 'quiser', 'disser',
           'tiver', 'qualquer', 'estiver', 'impuser',
           'sequer', 'puser', 'quaisquer', 'requer',
           'quer', 'vier', 'souber']

    def dashrepl(matchobj):
        onset = matchobj.groups()[0]
        vowel = matchobj.groups()[1]
        r = matchobj.groups()[2]
        original_word = f"{onset}{vowel}{r}"

        if original_word in exceptions:
            return original_word
        else:
            if vowel == 'a':
                return f"{onset}á"
            elif vowel == 'i':
                return f"{onset}í"
            elif vowel == 'e':
                if original_word in ehr:
                    return f"{onset}é"
                else:
                    return f"{onset}ê"

    for lab in labs:
        with open(lab, "r") as open_file:
            line = open_file.readline()
        s_pattern = re.compile(r"([a-zíúéóáôêâãõàç]*)([a-z])(r)\b")
        if s_pattern.search(line):
            line = s_pattern.sub(dashrepl, line)
        with open(lab, "w") as open_file:
            open_file.write(line)


def _modify_prep(input_dir):
    print("Modifying prepositions...")
    labs = _get_labs(input_dir)

    for lab in labs:
        with open(lab, "r") as open_file:
            line = open_file.readline()

        para = re.compile(r"\bpara\b")
        para_a = re.compile(r"\bpara a\b")
        para_as = re.compile(r"\bpara as\b")
        para_o = re.compile(r"\bpara o\b")
        para_os = re.compile(r"\bpara os\b")

        line = para_as.sub(r"pras", line)
        line = para_a.sub(r"pra", line)
        line = para_os.sub(r"pros", line)
        line = para_o.sub(r"pro", line)
        line = para.sub(r"pra", line)

        with open(lab, "w") as open_file:
            open_file.write(line)


def _modify_estar(input_dir):
    print("Modifying verb 'estar'...")
    labs = _get_labs(input_dir)

    for lab in labs:
        with open(lab) as open_file:
            line = open_file.readline()

        estou = re.compile(r"\bestou\b")
        esta = re.compile(r"\bestá\b")
        estamos = re.compile(r"\bestamos\b")
        estao = re.compile(r"\bestão\b")
        estava = re.compile(r"\bestava\b")
        estavam = re.compile(r"\bestavam\b")
        estive = re.compile(r"\bestive\b")
        esteve = re.compile(r"\besteve\b")
        estiveram = re.compile(r"\bestiveram\b")

        line = estou.sub(r"tô", line)
        line = esta.sub(r"tá", line)
        line = estamos.sub(r"tamo", line)
        line = estao.sub(r"tão", line)
        line = estava.sub(r"tava", line)
        line = estavam.sub(r"tavam", line)
        line = estive.sub(r"tive", line)
        line = esteve.sub(r"teve", line)
        line = estiveram.sub(r"tiveram", line)

        with open(lab, "w") as open_file:
            open_file.write(line)


def change(input_dir, ou_exceptions, r_exceptions):
    _modify_ou(input_dir, ou_exceptions)
    _modify_r(input_dir, r_exceptions)
    _modify_prep(input_dir)
    _modify_estar(input_dir)

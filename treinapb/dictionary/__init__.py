from pathlib import Path
import re
import treinapb.dictionary.wordlist_extractor as wl
import treinapb.dictionary.lexer


def gendict(inpath, outpath):

    word_list = wl.get_word_list(inpath)

    phonetic_words = []

    print("Creating phonemic dictionary...")

    for word in word_list:
        # print(word)
        # phonetic_words.append(word + " " + lexer.convert(word))
        try:
            phonetic_words.append(word + " " + treinapb.dictionary.lexer.convert(word))
        except IndexError:
            print(word)

    phonetic_dict = "\n".join(phonetic_words)

    new_file = open(outpath, "w")
    new_file.write(phonetic_dict)
    new_file.close()


def fixdict(dic):

    p = Path(dic)

    with open(p) as open_file:
        lines = open_file.readlines()

    print("Fixing dictionary...")

    ehi = re.compile(r'\beh I\b')
    ohi = re.compile(r'\boh I\b')
    sil = re.compile(r'\bsil\b')
    dz = re.compile(r'\bdZ\b')
    ts = re.compile(r'\btS\b')

    for index, line in enumerate(lines):
        if ehi.search(line):
            lines[index] = ehi.sub(r'eI', line)
    for index, line in enumerate(lines):
        if ohi.search(line):
            lines[index] = ohi.sub(r'oI', line)
    for index, line in enumerate(lines):
        if sil.search(line):
            lines[index] = sil.sub(r's i l', line)
    for index, line in enumerate(lines):
        if dz.search(line):
            lines[index] = dz.sub(r'd', line)
    for index, line in enumerate(lines):
        if ts.search(line):
            lines[index] = ts.sub(r't', line)

    for index, line in enumerate(lines):
        if re.search(" N", line):
            lines[index] = re.sub(" N", "", line)

    for index, line in enumerate(lines):
        if re.search(" EI", line):
            lines[index] = re.sub(" EI", " eI", line)

    for index, line in enumerate(lines):
        if re.search(" Z", line):
            lines[index] = re.sub(" Z", " s", line)

    for index, line in enumerate(list(lines)):
        if line == "\n":
            lines.remove(line)

    fixed = ''.join(lines)

    with open(p, 'w') as open_file:
        open_file.write(fixed)

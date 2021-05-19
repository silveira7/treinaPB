import re
from pathlib import Path
from collections import Counter


def get_words(labs):
    lines = list()
    words = list()
    for lab in labs:
        with open(lab) as open_file:
            lines.append(open_file.readline())
    for line in lines:
        for word in line.split(sep=' '):
            words.append(word)
    return words


def wordlist(words):
    word_list = list()
    words_count = sorted(Counter(words).items(),
                         key=lambda x: x[1],
                         reverse=True)
    for pair in words_count:
        word_list.append(f"{str(pair[1]):<10} {pair[0]}\n")
    return ''.join(word_list)


def special_wordlists(words):
    mono_ou = list()
    r_final = list()
    for word in words:
        if 'ou' in word:
            mono_ou.append(word)
        elif re.search(r'r\b', word):
            r_final.append(word)
    mono_ou = '\n'.join(set(mono_ou))
    r_final = '\n'.join(set(r_final))
    return [mono_ou, r_final]


def export_wordlists(wordlists, output_dir):
    output_dir = Path(output_dir)
    counter = 0
    for filename in ['mono_out.txt', 'r_final.txt', 'wordlist.txt']:
        with open(output_dir / filename, 'w') as open_file:
            open_file.write(wordlists[counter])
        counter += 1


def modify_ou(labs, exception_file):

    with open(exception_file) as open_file:
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
        with open(lab, 'r') as open_file:
            line = open_file.readline()
        s_pattern = re.compile(r'([a-z]*)(ou)([a-z]*)')
        if s_pattern.search(line):
            line = s_pattern.sub(dashrepl, line)
        with open(lab, 'w') as open_file:
            open_file.write(line)


def modify_r(labs, exception_file):

    with open(exception_file) as open_file:
        exceptions = open_file.readlines()

    for index, word in enumerate(exceptions):
        exceptions[index] = word[:-1]

    def dashrepl(matchobj):
        onset = matchobj.groups()[0]
        r = matchobj.groups()[1]
        original_word = f"{onset}{r}"
        modified_word = f"{onset}"

        if original_word in exceptions:
            return original_word
        else:
            return modified_word

    for lab in labs:
        with open(lab, 'r') as open_file:
            line = open_file.readline()
        s_pattern = re.compile(r'([a-z]*)(r)\b')
        if s_pattern.search(line):
            line = s_pattern.sub(dashrepl, line)
        with open(lab, 'w') as open_file:
            open_file.write(line)


def modify_prep(labs):
    for lab in labs:
        with open(lab, 'r') as open_file:
            line = open_file.readline()

        para = re.compile(r'\bpara\b')
        para_a = re.compile(r'\bpara a\b')
        para_as = re.compile(r'\bpara as\b')
        para_o = re.compile(r'\bpara o\b')
        para_os = re.compile(r'\bpara os\b')

        line = para_as.sub(r'pras', line)
        line = para_a.sub(r'pra', line)
        line = para_os.sub(r'pros', line)
        line = para_o.sub(r'pro', line)
        line = para.sub(r'pra', line)

        with open(lab, 'w') as open_file:
            open_file.write(line)


def modify_estar(labs):
    for lab in labs:
        with open(lab) as open_file:
            line = open_file.readline()

        estou = re.compile(r'\bestou\b')
        esta = re.compile(r'\bestá\b')
        estamos = re.compile(r'\bestamos\b')
        estao = re.compile(r'\bestão\b')
        estava = re.compile(r'\bestava\b')
        estavam = re.compile(r'\bestavam\b')
        estive = re.compile(r'\bestive\b')
        esteve = re.compile(r'\besteve\b')
        estiveram = re.compile(r'\bestiveram\b')

        line = estou.sub(r'tô', line)
        line = esta.sub(r'tá', line)
        line = estamos.sub(r'tamo', line)
        line = estao.sub(r'tão', line)
        line = estava.sub(r'tava', line)
        line = estavam.sub(r'tavam', line)
        line = estive.sub(r'tive', line)
        line = esteve.sub(r'teve', line)
        line = estiveram.sub(r'tiveram', line)

        with open(lab, 'w') as open_file:
            open_file.write(line)

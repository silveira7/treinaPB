import os
import re


def get_files(path):
    tg = []
    files = sorted(os.listdir(path))
    for file in files:
        if "TextGrid" in file:
            tg.append(path + file)
    return tg


def read_files(tg):
    for file in tg:
        with open(file) as opened_file:
            lines = opened_file.readlines()
        first_lim = 'Null'
        second_lim = 'Null'
        for index, line in enumerate(lines):
            if "item [2]" in line:
                first_lim = index
            elif "item [3]" in line:
                second_lim = index
        for index, line in enumerate(lines):
            if first_lim < index < second_lim:
                if "text" in line:
                    if "dZ" in line:
                        lines[index] = re.sub("dZ", "d", line)
                    if "tS" in line:
                        lines[index] = re.sub("tS", "t", line)
        edited = "".join(lines)
        with open(file, "w") as opened_file:
            opened_file.write(edited)


PATH = "/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/media_files/final/YasminS/YasminS_03/"

my_tg = get_files(PATH)
read_files(my_tg)

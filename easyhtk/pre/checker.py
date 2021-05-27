from pathlib import Path
import json
import enchant
import re
from termcolor import colored

br = enchant.Dict('pt_BR')


def checker(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    labs = sorted(list(input_dir.glob('*.lab')))
    waves = sorted(list(input_dir.glob('*.wav')))

    # Checar labs vazios
    empties = []
    for lab in labs:
        if lab.stat().st_size == 0:
            empties.append(lab.name)

    if not empties:
        print(f'Nenhum arquivo .lab vazio [{colored("VERDADE", "green")}].')
    else:
        print(f'Nenhum arquivo .lab vazio [{colored("FALSO", "red")}].')
        with open(output_dir / "empties.json", 'w') as opened_file:
            opened_file.write(json.dumps(empties, indent=4))

    # Checar áudios quebrados
    broken = []
    for wav in waves:
        if wav.stat().st_size < 1000:
            broken.append(wav.name)

    if not broken:
        print(f'Nenhum arquivo .wav corrompido [{colored("VERDADE", "green")}].')
    else:
        print(f'Nenhum arquivo .wav corrompido [{colored("FALSO", "red")}].')
        with open(output_dir / "brokens.json", 'w') as opened_file:
            opened_file.write(json.dumps(broken, indent=4))

    # Checar se há arquivos com mais de uma linha
    not_one_line = []
    for lab in labs:
        with open(lab, 'r') as open_file:
            lines = open_file.readlines()
        if len(lines) > 1:
            not_one_line.append(lab.name)

    if not not_one_line:
        print(f'Nenhum arquivo .lab com mais de uma linha [{colored("VERDADE", "green")}].')
    else:
        print(f'Nenhum arquivo .lab com mais de uma linha [{colored("FALSO", "red")}].')
        with open(output_dir / "more_lines.json", 'w') as opened_file:
            opened_file.write(json.dumps(not_one_line, indent=4))

    # Checar se há lab sem wav correspondente
    lab_with_no_wav = []
    for lab in labs:
        if not lab.with_suffix('.wav').exists():
            lab_with_no_wav.append(lab.name)

    if not lab_with_no_wav:
        print(f'Nenhum arquivo .lab sem .wav correspondente [{colored("VERDADE", "green")}].')
    else:
        print(f'Nenhum arquivo .lab sem .wav correspondente [{colored("FALSO", "red")}].')
        with open(output_dir / "with_no_wav.json", 'w') as opened_file:
            opened_file.write(json.dumps(lab_with_no_wav, indent=4))

    # Checar se há wav sem lab correspondente
    wav_with_no_lab = []
    for wav in waves:
        if not wav.with_suffix('.lab').exists():
            wav_with_no_lab.append(wav.name)

    if not wav_with_no_lab:
        print(f'Nenhum arquivo .wav sem .lab correspondente [{colored("VERDADE", "green")}].')
    else:
        print(f'Nenhum arquivo .wav sem .lab correspondente [{colored("FALSO", "red")}].')
        with open(output_dir / "with_no_lab.json", 'w') as opened_file:
            opened_file.write(json.dumps(wav_with_no_lab, indent=4))

    # Checar se há lab apenas com espaços
    only_spaces = []
    for lab in labs:
        with open(lab, 'r') as open_file:
            lines = open_file.readlines()
        for line in lines:
            if re.search(r'^ +$', line):
                only_spaces.append(lab.name)
                break

    if not only_spaces:
        print(f'Nenhum arquivo .lab apenas com espaços [{colored("VERDADE", "green")}].')
    else:
        print(f'Nenhum arquivo .wav apenas com espaços [{colored("FALSO", "red")}].')
        with open(output_dir / "only_spaces.json", 'w') as opened_file:
            opened_file.write(json.dumps(only_spaces, indent=4))

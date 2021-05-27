import sys
from pathlib import Path


def verify(input_dir):
    p = Path(input_dir)
    labs = list(p.glob('*.lab'))

    groups = dict()

    for lab in labs:
        speaker = lab.stem.split(sep='_')[1]
        if speaker not in groups.keys():
            groups[speaker] = []
        else:
            continue

    for speaker in groups.keys():
        for lab in labs:
            if speaker in lab.stem:
                if 'Isolated' in lab.stem:
                    groups[speaker].append(lab.stem)
                else:
                    group = '_'.join(lab.stem.split(sep='_')[0:3])
                    if group not in groups[speaker]:
                        groups[speaker].append(group)
                    else:
                        continue

    for speaker, grps in groups.items():
        print(speaker, len(grps))


input_directory = sys.argv[1]
verify(input_directory)

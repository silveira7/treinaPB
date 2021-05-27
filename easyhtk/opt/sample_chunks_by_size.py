from pathlib import Path
import random


def _get_labs(input_dir):
    p = Path(input_dir)
    labs = list(p.glob('*.lab'))
    return labs


def _get_speakers(input_dir):
    print('Getting list of speakers...')
    labs = _get_labs(input_dir)
    groups = dict()
    for lab in labs:
        speaker = lab.stem.split(sep='_')[1]
        if speaker not in groups.keys():
            groups[speaker] = []
        else:
            continue
    return groups


def _get_groups(input_dir, groups):
    print('Getting groups...')
    labs = _get_labs(input_dir)
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
    return groups


def _sample(input_dir, groups):
    print('Sampling...')
    p = Path(input_dir)
    directory_size = 0
    new_directory = p / 'selection'
    new_directory.mkdir(exist_ok=True)
    # while directory_size < 1000 * 1000 * 1000:
    while directory_size < 1000000:
        for speaker in groups.keys():
            print(f'Sampling group from speaker {speaker}...')
            try:
                chosen_group = random.choice(groups[speaker])
            except IndexError:
                print(f'No more groups for speaker {speaker}...')
                continue
            groups[speaker].remove(chosen_group)
            group_files = sorted(list(p.glob(f'*{chosen_group}*')))
            group_size = 0
            for file in group_files:
                group_size += file.stat().st_size
                new_path = new_directory / file.name
                file.rename(new_path)
            directory_size += group_size


def sample_chunks(input_dir):
    groups = _get_speakers(input_dir)
    groups = _get_groups(input_dir, groups)
    _sample(input_dir, groups)

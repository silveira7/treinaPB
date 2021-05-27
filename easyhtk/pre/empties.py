from pathlib import Path


def remove_empties(input_dir):
    p = Path(input_dir)
    labs = sorted(list(p.glob('*.lab')))
    to_remove = []
    for lab in labs:
        if lab.stat().st_size == 0:
            if 'Isolated' in lab.name:
                group_id = '_'.join(lab.name.split(sep='_')[0:4])
            else:
                group_id = '_'.join(lab.name.split(sep='_')[0:3])

            group_files = list(Path(input_dir).glob(f'{group_id}*'))

            for file in group_files:
                to_remove.append(file)

    for file in to_remove:
        file.unlink(missing_ok=True)

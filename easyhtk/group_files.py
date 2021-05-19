from pathlib import Path


path = Path("/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/media_files/final/")

# get_files
p = Path(path)
files = sorted(list(p.glob('*.wav')))


# get_speakers
speakers = []
for file in files:
    speaker = file.stem.split(sep='_')[2]
    if speaker not in speakers:
        speakers.append(speaker)


# create_speakers_dir
for speaker in speakers:
    speaker_dir = path / speaker
    speaker_dir.mkdir(exist_ok=True)


# move_files
for speaker in speakers:

    speaker_files = []
    for file in files:
        if speaker in file.name:
            speaker_files.append(file)

    counter = 0
    dir_num = 0
    for file in speaker_files:

        if counter == 0:
            counter += 1
            dir_num += 1
            dir_num_str = str(dir_num).zfill(2)
            folder_name = f'{speaker}_{dir_num_str}'
            folder_path = file.parent / speaker / folder_name
            folder_path.mkdir(exist_ok=True)
            tg = file.with_suffix('.TextGrid')
            file.rename(folder_path / file.name)
            tg.rename(folder_path / tg.name)
        elif counter < 100:
            counter += 1
            tg = file.with_suffix('.TextGrid')
            file.rename(folder_path / file.name)
            tg.rename(folder_path / tg.name)
        elif counter == 100:
            counter = 0
            tg = file.with_suffix('.TextGrid')
            file.rename(folder_path / file.name)
            tg.rename(folder_path / tg.name)

import os
from pathlib import Path


def get_files(path):
    files = sorted(os.listdir(path))
    wav_files = []
    for file in files:
        if ".wav" in file:
            wav_files.append(path + file)
    return wav_files


def create_folder(path):
    try:
        new_dir_path = os.path.join(path, 'broken_audios')
        os.mkdir(new_dir_path)
    except FileExistsError:
        print('Folder not created because it already exists.')


def filter_by_weight(wav_files):
    for file in wav_files:
        p = Path(file)
        if p.stat().st_size < 100:
            print(f"Moving {p.name}")
            dst = p.parent / "broken_audios" / p.name
            p.rename(dst)
            src = p.with_suffix(".TextGrid")
            dst = p.parent / "broken_audios" / src.name
            src.rename(dst)


my_path = "/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/media_files/final/"

create_folder(my_path)

my_waves = get_files(my_path)
filter_by_weight(my_waves)


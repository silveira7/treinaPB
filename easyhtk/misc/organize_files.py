"""This module moves the files of each speaker to a separated folder"""

from pathlib import Path


def organize(folder):
    p = Path(folder)

    p_intervals = p / 'intervals'
    p_final = p / 'final'

    p_intervals.mkdir(exist_ok=True)
    p_final.mkdir(exist_ok=True)

    for path in p.iterdir():
        if path.is_file():
            if path.match('*merged.TextGrid'):
                path.rename(p_final / path.name)
            elif path.match('*Isolated*.TextGrid'):
                iso_filename = '_'.join(path.name.split(sep='_')[0:5]) + '.TextGrid'
                path.rename(p_final / iso_filename)
            else:
                path.rename(p_intervals / path.name)


organize('/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/media_files/')

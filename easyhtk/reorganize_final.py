from pathlib import Path
import re

p = Path("/home/gustavo/Documentos/Universidade/Dados/Projeto_Acomodacao/ALCP/media_files/final/")

original_files = list()

for file in p.iterdir():
    if file.is_dir() and 'broken' not in file.name:
        for sub_dir in file.iterdir():
            for sub_sub_dir in sub_dir.iterdir():
                if sub_sub_dir.is_file():
                    if re.search(r"Isolated_\d+\.", sub_sub_dir.name):
                        original_files.append(sub_sub_dir)

original_files = sorted(original_files)

dest_path = Path("/home/gustavo/Documentos/Corpora/ALCP/Chunks/")

for file in original_files:
    foldername = file.name.split("_")[2]
    dest = dest_path / foldername / file.name
    file.rename(dest)

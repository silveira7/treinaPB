"""This script duplicates the TextGrids and mark the duplicate with
_unmod"""

from pathlib import Path
import shutil

directory = "/home/gustavo/Documentos/Corpora/ALCP/Chunks/"

p = Path(directory)

# for file in p.iterdir():
#     selection_dir = file / "Selection"
#     for sub_file in selection_dir.iterdir():
#         if sub_file.match('*.TextGrid'):
#             new_name = sub_file.stem + "_unmod.TextGrid "
#             shutil.copy(sub_file, sub_file.with_name(new_name))

for file in p.iterdir():
    selection_dir = file / "Selection"
    unmod_dir = selection_dir / "Unmodified_TextGrids"
    unmod_dir.mkdir(exist_ok=True)
    for sub_file in selection_dir.iterdir():
        if sub_file.match('*unmod*'):
            sub_file.rename(unmod_dir / sub_file.name)

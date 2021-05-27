from pathlib import Path

p = Path('/home/gustavo/Drive/Repositorios/speech-align-tools/test/final/')

for path in p.iterdir():
    for sub_path in path.glob('*.TextGrid'):
        new_name = sub_path.stem + '_orig'
        sub_path.rename(sub)

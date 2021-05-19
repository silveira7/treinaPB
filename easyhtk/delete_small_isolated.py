from pathlib import Path
import wave
import contextlib


p = Path("/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/media_files/final/isolat/")


for file in p.iterdir():
    if file.suffix == ".wav":
        with contextlib.closing(wave.open(str(file), 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            if duration < 4:
                tg = file.parent / file.with_suffix(".TextGrid")
                file.unlink()
                tg.unlink()

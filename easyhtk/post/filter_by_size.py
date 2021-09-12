from pathlib import Path
import wave
import contextlib


def filter(input_dir):
    p = Path(input_dir)
    waves = list(p.glob('*.wav'))

    less_than_four = p / 'less_than_four'
    more_than_six = p / 'more_than_six'
    in_between = p / 'in_between'

    less_than_four.mkdir(exist_ok=True)
    more_than_six.mkdir(exist_ok=True)
    in_between.mkdir(exist_ok=True)

    num_less_than_four = 0
    num_more_than_six = 0
    num_in_between = 0

    for wav in waves:
        with contextlib.closing(wave.open(str(wav), 'r')) as open_wav:
            frames = open_wav.getnframes()
            rate = open_wav.getframerate()
            duration = frames / float(rate)

        textgrid = wav.with_suffix('.TextGrid')

        if duration < 4:
            num_less_than_four += 1
            new_wav_path = less_than_four / wav.name
            new_textgrid_path = less_than_four / textgrid.name
            wav.rename(new_wav_path)
            textgrid.rename(new_textgrid_path)
        elif duration > 6:
            num_more_than_six += 1
            new_wav_path = more_than_six / wav.name
            new_textgrid_path = more_than_six / textgrid.name
            wav.rename(new_wav_path)
            textgrid.rename(new_textgrid_path)
        else:
            num_in_between += 1
            new_wav_path = in_between / wav.name
            new_textgrid_path = in_between / textgrid.name
            wav.rename(new_wav_path)
            textgrid.rename(new_textgrid_path)

    print(f'Less than 4 seconds: {str(num_less_than_four)} \n',
          f'More than 6 seconds: {str(num_more_than_six)} \n',
          f'In between: {str(num_in_between)} \n')

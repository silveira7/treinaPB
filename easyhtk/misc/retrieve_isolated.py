import os
from pydub import AudioSegment

def get_filenames(path):
    files = os.listdir(path)
    isolated = []
    for file in files:
        if 'Isolated' in file and '.lab' in file:
            isolated.append(file)
    return isolated


def get_info(isolated):
    info = {}
    for filename in isolated:
        speaker = filename.split(sep='_')[2]
        annotation, begin_time, end_time = filename.split(sep='_')[4:]
        end_time = end_time[:-4]
        if speaker not in info.keys():
            info[speaker] = [[annotation, begin_time, end_time]]
        else:
            info[speaker].append([annotation, begin_time, end_time])
    return info


def get_wav_files(folder):
    wav_files = []
    files = os.listdir(folder)
    for file in files:
        if '.wav' in file:
            wav_files.append(file)
    return wav_files


def extract_audio(info, wav_files, orig_folder, destination):
    for speaker, intervals in info.items():
        for wav in wav_files:
            if speaker in wav:
                print('Loading audio...')
                audio_path = os.path.join(orig_folder, wav)
                audio = AudioSegment.from_wav(audio_path)
                print('Audio successfully loaded...')
                for interval in intervals:
                    print(f'Slicing {speaker}, {interval}')
                    interval_audio_filename = f'{wav[:-4]}_Isolated_{interval[0]}.wav'
                    interval_slice_dest = os.path.join(destination, interval_audio_filename)
                    interval_slice = audio[int(interval[1]): int(interval[2])]
                    interval_slice.export(interval_slice_dest, format='wav')
    print('Extraction concluded!')


my_dir = '/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/media_files/intervals'
my_orig_dir = '/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/'
my_dest = '/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/media_files/final/'

iso = get_filenames(my_dir)
inf = get_info(iso)
my_waves = get_wav_files(my_orig_dir)
extract_audio(inf, my_waves, my_orig_dir, my_dest)

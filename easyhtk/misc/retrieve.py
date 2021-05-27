import os
import re
from pydub import AudioSegment


def get_tg(path):
    files = sorted(os.listdir(path))
    tg = []
    for file in files:
        if 'TextGrid' in file:
            tg.append(file)
    tg = list(set(tg))
    return sorted(tg)


def get_group(tg):
    info = {}
    for file in tg:
        speaker, group, annotation_id = file.split(sep="_")[2:5]
        if speaker not in info.keys():
            info[speaker] = {group: [annotation_id]}
        elif group not in info[speaker].keys():
            info[speaker][group] = [annotation_id]
        else:
            info[speaker][group].append(annotation_id)
    return info


def get_boundary(info):
    boundaries = {}
    for speaker, groups in info.items():
        for group, annotations in groups.items():
            if speaker not in boundaries.keys():
                boundaries[speaker] = {group: [annotations[0], annotations[-1]]}
            elif group not in boundaries[speaker].keys():
                boundaries[speaker][group] = [annotations[0], annotations[-1]]
    return boundaries


def get_times(boundaries, tg):
    for speaker, groups in boundaries.items():
        for group_id, bound in groups.items():
            first_bound = f'_{bound[0]}_'
            second_bound = f'_{bound[1]}_'
            begin_time = end_time = 0
            for file in tg:
                if speaker in file:
                    if first_bound in file:
                        begin_time = file.split(sep="_")[5]
                    elif second_bound in file:
                        end_time = file.split(sep="_")[6][0:-9]
            if begin_time == 0:
                print('Problem!')
            elif end_time == 0:
                print('Problem!')
            groups[group_id] = [begin_time, end_time]
    return boundaries


def get_orig_filenames(orig_folder):
    wav_files = [x for x in os.listdir(orig_folder) if '.wav' in x]
    return wav_files


def extract_audios(updated_boundaries, wav_files, orig_folder, destination):
    print(updated_boundaries)
    for speaker, groups in updated_boundaries.items():
        for wav_file in wav_files:
            if speaker in wav_file:
                print('Loading audio...')
                audio_path = os.path.join(orig_folder, wav_file)
                audio = AudioSegment.from_wav(audio_path)
                print('Audio successfully loaded...')
                for group, bounds in groups.items():
                    print(f'Slicing {speaker}, {group}')
                    group_filename = f'{wav_file[0:-4]}_{group}_merged.wav'
                    group_slice_dest = os.path.join(destination, group_filename)
                    group_slice = audio[int(bounds[0]): int(bounds[1])]
                    group_slice.export(group_slice_dest, format="wav")
    print("Extraction completed.")


def batch_retrieve(folder, orig_folder, destination):
    tg = get_tg(folder)
    info = get_group(tg)
    boundaries = get_boundary(info)
    boundaries = get_times(boundaries, tg)
    wav_files = get_orig_filenames(orig_folder)
    extract_audios(boundaries, wav_files, orig_folder, destination)


my_dir = '/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/media_files/intervals/'
orig = '/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/'
dest = '/home/gustavo/Drive/Universidade/Dados/Projeto_Acomodacao/ALCP/media_files/final/'

batch_retrieve(my_dir, orig, dest)

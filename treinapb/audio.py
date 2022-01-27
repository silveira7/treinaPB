from pathlib import Path
from pydub import AudioSegment


def get_waves(input_dir):
    input_dir = Path(input_dir)
    waves = sorted(list(input_dir.glob('*.wav')))
    for wav in list(waves):
        if 'Isolated' in wav.name:
            waves.remove(wav)
    return waves


def get_info(waves):
    info = {}
    for wav in waves:
        speaker, group, annotation_id = wav.name.split(sep="_")[1:4]
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


def get_times(boundaries, waves):
    for speaker, groups in boundaries.items():
        for group_id, bound in groups.items():
            first_bound = f'_{bound[0]}_'
            second_bound = f'_{bound[1]}_'
            begin_time = end_time = 0
            for file in waves:
                if speaker in file.name:
                    if first_bound in file.name:
                        begin_time = file.name.split(sep="_")[4]
                    elif second_bound in file.name:
                        end_time = file.name.split(sep="_")[5][0:-4]
            if begin_time == 0:
                print('Problem!')
            elif end_time == 0:
                print('Problem!')
            groups[group_id] = [begin_time, end_time]
    return boundaries


def get_orig_filenames(orig_folder):
    orig_wav_files = sorted(list(Path(orig_folder).glob('*.wav')))
    return orig_wav_files


def extract_audios(updated_boundaries, wav_files, destination):
    destination = Path(destination)
    for speaker, groups in updated_boundaries.items():
        for wav_file in wav_files:
            if speaker in wav_file.name:
                print('Loading audio...')
                audio = AudioSegment.from_wav(wav_file)
                print('Audio successfully loaded...')
                for group, bounds in groups.items():
                    print(f'Slicing {speaker}, {group}')
                    group_filename = f'{wav_file.name[0:-4]}_{group}_merged.wav'
                    group_slice_dest = destination / group_filename
                    group_slice = audio[int(bounds[0]): int(bounds[1])]
                    group_slice.export(group_slice_dest, format="wav")
    print("Extraction completed.")

def retrieve(input_dir):
    p = Path(input_dir)
    waves = sorted(list(p.glob('*.wav')))
    group_done = []

    print('Merging .wav files...')
    for wav in waves:
        if 'Isolated' not in wav.name:
            file_info = wav.name.split(sep='_')[0:3]
            group_id = '_'.join(file_info)
            if group_id not in group_done:

                group_done.append(group_id)
                group_waves = sorted(list(p.glob(f'*{group_id}*.wav')))
                for index, each_wav in enumerate(group_waves):
                    if index == 0:
                        merged_waves = AudioSegment.from_wav(each_wav)
                    else:
                        merged_waves += AudioSegment.from_wav(each_wav)
                filepath = p / f'{group_id}_merged.wav'
                merged_waves.export(filepath, format="wav")

def batch_retrieve(input_dir, orig_folder):
    waves = get_waves(input_dir)
    info = get_info(waves)
    boundaries = get_boundary(info)
    boundaries = get_times(boundaries, waves)
    orig_files = get_orig_filenames(orig_folder)
    extract_audios(boundaries, orig_files, input_dir)

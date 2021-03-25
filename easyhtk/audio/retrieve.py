import os
import re
import json
from pydub import AudioSegment


def retrieve(folder, orig_folder):

    files = sorted(os.listdir(folder))

    tg = []
    for file in files:
        if 'TextGrid' in file:
            tg.append(file)

    info = {}

    for file in tg:
        speaker, group, annotation_id = file.split(sep="_")[2:5]
        if speaker not in info.keys():
            info[speaker] = {group: [annotation_id]}
        elif group not in info[speaker].keys():
            info[speaker][group] = [annotation_id]
        else:
            info[speaker][group].append(annotation_id)

    times = {}

    for speaker, groups in info.items():
        for group, annotations in groups.items():
            if speaker not in times.keys():
                times[speaker] = {group: [annotations[0], annotations[-1]]}
            elif group not in times[speaker].keys():
                times[speaker][group] = [annotations[0], annotations[-1]]

    begin = None
    end = None

    for speaker, groups in times.items():
        for group, notes in groups.items():
            for file in tg:
                if speaker in file and notes[0] in file:
                    begin = file.split(sep="_")[5]
                if speaker in file and notes[1] in file:
                    end = file.split(sep="_")[6][0:-9]
            groups[group] = [begin, end]
            print(speaker, group, begin, end)

    times_json = json.dumps(times)

    new_file = open(os.path.join(orig_folder, "groups_info.json"), "w")
    new_file.write(times_json)
    new_file.close()

    wav_files = []

    for file in os.listdir(orig_folder):
        if re.search(r'.wav', file):
            wav_files.append(file)

    for file in wav_files:
        print(f"Loading {file}.")
        audio = AudioSegment.from_wav(orig_folder + file)
        print("Loaded.")
        for speaker, groups in times.items():
            new_file_path = f"{orig_folder}media_files/final/{speaker}/"
            if speaker in file:
                for group, notes in groups.items():
                    print(f"Extracting audio - group {group}, speaker {speaker}.")
                    interval = audio[int(notes[0]): int(notes[1])]
                    group_file_name = f"{file[0:-4]}_{group}_merged.wav"
                    interval.export(new_file_path + group_file_name, format="wav")

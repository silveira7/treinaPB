import os
import re


def import_textgrids(folder):
    files = sorted(os.listdir(folder))
    textgrids = []
    for file in files:
        if ".TextGrid" in file:
            textgrids.append(file)
    return textgrids


def _add_utterance(note_id, group, begin, end):
    return {'identity': note_id,
            'group': group,
            'begin': begin,
            'end': end,
            'tiers': []}


def _add_speaker(data, speaker, note_id, group, begin, end):
    data['speakers'].append({'speaker': speaker,
                             'utterances': [
                                 _add_utterance(note_id, group, begin, end)
                             ]})


def _get_filename_info(filename):
    speaker, group, note_id, begin, end \
        = filename.split(sep='_')[2:]

    return [
        speaker, int(group), int(note_id[1:]),
        int(begin), int(end[0:-9])
    ]


def extract_info_from_filename(textgrids):
    speakers_tracker = []
    data = {'category': 'TextGrids',
            'speakers': [
                {
                    'speaker': '',
                    'utterances': []
                }
            ]}

    for textgrid in textgrids:
        speaker, group, note_id, begin, end \
            = _get_filename_info(textgrid)

        if not data['speakers'][0]['speaker']:
            speakers_tracker.append(speaker)
            data['speakers'][0]['speaker'] = speaker
            data['speakers'][0]['utterances'].append(
                _add_utterance(note_id, group, begin, end)
            )

        elif speaker not in speakers_tracker:
            speakers_tracker.append(speaker)
            _add_speaker(data, speaker, note_id, group, begin, end)

        else:
            for speaker_dict in data['speakers']:
                if speaker_dict['speaker'] == speaker:
                    speaker_dict['utterances'].append(
                        _add_utterance(note_id, group, begin, end)
                    )
    return data


def _extract_tiers(textgrid, data, speaker, note_id):
    for index, line in enumerate(textgrid):
        item_rgx = re.compile(r'item \[(\d)]')
        name_rgx = re.compile(r'\"(.*)\"')
        min_max_rgx = re.compile(r'\d+\.\d+')

        if item_rgx.search(line):
            item = int(item_rgx.search(line).groups()[0])
            name = name_rgx.search(textgrid[index + 2]).groups()[0]
            xmin = float(min_max_rgx.search(textgrid[index + 3]).group())
            xmax = float(min_max_rgx.search(textgrid[index + 4]).group())
            size = int(re.search(r'\d+', textgrid[index + 5]).group())

            for speaker_dict in data['speakers']:
                if speaker_dict['speaker'] == speaker:
                    for utterance in speaker_dict['utterances']:
                        if utterance['identity'] == note_id:
                            utterance['tiers'].append(
                                dict(item=item,
                                     name=name,
                                     xmin=xmin,
                                     xmax=xmax,
                                     size=size,
                                     intervals=[], )
                            )


def _search_intervals_info(index, line, utterance, tier_name, tier_number):
    if 'intervals [' in line:
        number = int(re.search(r'intervals \[(\d+)]',
                               line).groups()[0])
        xmin = float(re.search(r'(\d+\.\d+)',
                               tier_name[index + 1]).groups()[0])
        xmax = float(re.search(r'(\d+\.\d+)',
                               tier_name[index + 2]).groups()[0])
        text = re.search(r'\"(.*)\"',
                         tier_name[index + 3]).groups()[0]

        utterance['tiers'][tier_number]['intervals'].append(
            dict(number=number, xmin=xmin, xmax=xmax, text=text))


def _extract_intervals(textgrid, data, speaker, note_id):
    boundary = None

    for index, line in enumerate(textgrid):
        item_rgx = re.compile(r'item \[(\d)]')
        if item_rgx.search(line):
            boundary = index

    first_tier = textgrid[8:boundary]
    second_tier = textgrid[boundary:]

    for speaker_dict in data['speakers']:
        if speaker_dict['speaker'] == speaker:
            for utterance in speaker_dict['utterances']:
                if utterance['identity'] == note_id:
                    for index, line in enumerate(first_tier):
                        _search_intervals_info(index, line, utterance,
                                               first_tier, 0)
                    for index, line in enumerate(second_tier):
                        _search_intervals_info(index, line, utterance,
                                               second_tier, 1)


def extract_from_textgrid(files_list, folder, data):
    for file in files_list:
        speaker = _get_filename_info(file)[0]
        note_id = _get_filename_info(file)[2]

        with open(os.path.join(folder, file)) as opened_file:
            textgrid = opened_file.readlines()

        _extract_tiers(textgrid, data, speaker, note_id)
        _extract_intervals(textgrid, data, speaker, note_id)
    return data

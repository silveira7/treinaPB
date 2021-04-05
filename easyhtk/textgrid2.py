import os
import re
import json
import copy


def import_textgrids(folder):
    files = sorted(os.listdir(folder))
    textgrids = []
    for file in files:
        if ".TextGrid" in file:
            textgrids.append(file)
    return textgrids


def add_utterance(note_id, group, begin, end):
    return {'identity': note_id,
            'group': group,
            'begin': begin,
            'end': end,
            'tiers': []}


def add_speaker(data, speaker, note_id, group, begin, end):
    data['speakers'].append({'speaker': speaker,
                             'utterances': [
                                 add_utterance(note_id, group, begin, end)
                             ]})


def get_filename_info(filename):
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
            = get_filename_info(textgrid)

        if not data['speakers'][0]['speaker']:
            speakers_tracker.append(speaker)
            data['speakers'][0]['speaker'] = speaker
            data['speakers'][0]['utterances'].append(
                add_utterance(note_id, group, begin, end)
            )

        elif speaker not in speakers_tracker:
            speakers_tracker.append(speaker)
            add_speaker(data, speaker, note_id, group, begin, end)

        else:
            for speaker_dict in data['speakers']:
                if speaker_dict['speaker'] == speaker:
                    speaker_dict['utterances'].append(
                        add_utterance(note_id, group, begin, end)
                    )
    return data


def get_tiers(number, name, xmin, xmax, size):
    return {
        "number": number,
        "name": name,
        "xmin": xmin,
        "xmax": xmax,
        "size": size,
        "intervals": []
    }


def extract_tiers(textgrid, data, speaker, note_id):
    for index, line in enumerate(textgrid):
        item_rgx = re.compile(r'item \[(\d)]')
        name_rgx = re.compile(r'\"(.*)\"')
        min_max_rgx = re.compile(r'\d+\.\d+')

        if item_rgx.search(line):
            item = int(item_rgx.search(line).groups()[0])
            name = name_rgx.search(textgrid[index+2]).groups()[0]
            xmin = float(min_max_rgx.search(textgrid[index+3]).group())
            xmax = float(min_max_rgx.search(textgrid[index+4]).group())
            size = int(re.search(r'\d+', textgrid[index+5]).group())

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
                                     intervals=[],)
                            )


def search_intervals_info(index, line, utterance, tier_name, tier_number):
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


def extract_intervals(textgrid, data, speaker, note_id):
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
                        search_intervals_info(index, line, utterance,
                                              first_tier, 0)
                    for index, line in enumerate(second_tier):
                        search_intervals_info(index, line, utterance,
                                              second_tier, 1)


def extract_from_textgrid(files_list, folder, data):
    for file in files_list:
        speaker = get_filename_info(file)[0]
        note_id = get_filename_info(file)[2]

        with open(os.path.join(folder, file)) as opened_file:
            textgrid = opened_file.readlines()

        extract_tiers(textgrid, data, speaker, note_id)
        extract_intervals(textgrid, data, speaker, note_id)
    return data


# def add_interval_to_list(utterance, merged_1st_tier, merged_2nd_tier,
#                          counter_1st, counter_2nd):
#     for interval in utterance['tiers'][0]['intervals']:
#         counter_1st += 1
#         merged_1st_tier.append(
#             f"""
#             \t\t\tintervals [{counter_1st}]:
#             \t\t\t\txmin = {interval['xmin']}
#             \t\t\t\txmax = {interval['xmax']}
#             \t\t\t\ttext = \"{interval['text']}\"
#             """
#         )
#     for interval in utterance['tiers'][1]['intervals']:
#         counter_2nd += 1
#         merged_2nd_tier.append(
#             f"""
#               \t\t\tintervals [{counter_2nd}]:
#               \t\t\t\txmin = {interval['xmin']}
#               \t\t\t\txmax = {interval['xmax']}
#               \t\t\t\ttext = \"{interval['text']}\"
#               """
#         )

def merge_textgrids(data):
    first_utter = True
    counter_1st = 0
    counter_2nd = 0
    max_adder = 0
    group_checker = None

    merged_1st_tier = []
    merged_2nd_tier = []

    for speaker in data['speakers']:
        for utterance in speaker['utterances']:
            if first_utter:
                first_utter = False
                group_checker = utterance['group']
                max_adder += utterance['tiers'][0]['xmax']

                for interval in utterance['tiers'][0]['intervals']:
                    counter_1st += 1
                    merged_1st_tier.append(f"""
\t\t\tintervals [{counter_1st}]:
\t\t\t\txmin = {interval['xmin']}
\t\t\t\txmax = {interval['xmax']}
\t\t\t\ttext = \"{interval['text']}\"
""")
                for interval in utterance['tiers'][1]['intervals']:
                    counter_2nd += 1
                    merged_2nd_tier.append(f"""
\t\t\tintervals [{counter_2nd}]:
\t\t\t\txmin = {interval['xmin']}
\t\t\t\txmax = {interval['xmax']}
\t\t\t\ttext = \"{interval['text']}\"
""")
            else:
                if utterance['group'] == group_checker:
                    for interval in utterance['tiers'][0]['intervals']:
                        counter_1st += 1
                        merged_1st_tier.append(f"""
\t\t\tintervals [{counter_1st}]:
\t\t\t\txmin = {interval['xmin']+max_adder}
\t\t\t\txmax = {interval['xmax']+max_adder}
\t\t\t\ttext = \"{interval['text']}\"
""")
                    for interval in utterance['tiers'][1]['intervals']:
                        counter_2nd += 1
                        merged_2nd_tier.append(f"""
\t\t\tintervals [{counter_2nd}]:
\t\t\t\txmin = {interval['xmin']+max_adder}
\t\t\t\txmax = {interval['xmax']+max_adder}
\t\t\t\ttext = \"{interval['text']}\"
""")

    for x in merged_1st_tier:
        print(x)




    # group_tracker = []
    #
    # for speaker in data['speakers']:
    #     for utterance in speaker['utterances']:
    #         if f"{speaker['speaker']}_{utterance['group']}" not in group_tracker:
    #             group_tracker.append(f"{speaker['speaker']}_{utterance['group']}")
    #             # group_tracker.append(utterance['group'])
    #
    # print(group_tracker)
    #         # xmax += utterance['tiers'][0]['xmax']

    # header = 'File type = "ooTextFile"\n' \
    #          + 'Object class = "TextGrid"\n' \
    #          + '\n' \
    #          + 'xmin = 0.0\n' \
    #          + 'xmax = ' + str("{:.2f}".format(xmax)) + '\n' \
    #          + 'tiers? <exists>\n' \
    #          + 'size = 2\n' \
    #          + 'item []:\n'
    # print(make_header(data, 1))
    # get_xmax(data)



path = '/home/gustavo/Drive/Repositorios/speech-align-tools/test/'

tgs = import_textgrids(path)

tg_data = extract_info_from_filename(tgs)

tg_data = extract_from_textgrid(tgs, path, tg_data)

merge_textgrids(tg_data)

new_file = open("tg_data.json", "w")
new_file.write(json.dumps(tg_data, indent=4))
new_file.close()

import os
import re
import nltk


def get_word_list(path):

    file_list = []

    for root, d_names, f_names in os.walk(path):
        for name in f_names:
            if re.search(r'.*\.lab', name):
                file_list.append(os.path.join(root, name))

    sentences_list = list()

    for file in file_list:
        with open(file) as file_text:
            sentences_list.append(file_text.read())

    merged_sentences = " ".join(sentences_list)
    tokens = nltk.word_tokenize(merged_sentences)
    words = []

    for token in tokens:
        if re.search(r'\w', token) \
                and not re.search(r'/', token) \
                and not re.search(r'xxx', token) \
                and not re.search(r'\.', token) \
                and not re.search(r'\d', token):
            words.append(token.lower())

    words = set(words)
    words = list(words)
    words.sort()

    return words

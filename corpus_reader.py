"""This module supplies an corpus document iterrator and functions to handle 1-of-N encoding."""

from collections import Counter
from itertools import chain
import json
import os
import string

import numpy as np

PATH_TO_CORPUS = os.path.expanduser('~/deepfanfic_corpus')

def get_corpus_iterrator(include_meta=True):
    """Itterates over the fanfiction corpus and returns documents represented as a list of words.

    Only acii letters are included in the list, also punctuation and digits are excluded."""

    for folder_name in os.listdir(PATH_TO_CORPUS):
        path = PATH_TO_CORPUS + '/' + folder_name
        story_path = path + '/stories'
        meta_path = path + '/meta'

        if not os.path.isdir(story_path):
            continue

        for doc_name in os.listdir(story_path):

            with open(story_path + '/' + doc_name) as f:
                text = f.read()

            word_list = to_machine_readable(text)

            if not include_meta:
                yield word_list
            else:
                name = os.path.splitext(doc_name)[0] + '.json'
                try:
                    with open(meta_path + '/' + name) as f:
                        json_code = f.read()
                    meta = json.loads(json_code)
                except:
                    meta = None
                yield (word_list, meta)


def to_machine_readable(text):
    valid_chars = string.ascii_letters + string.whitespace #+ string.digits
    text = ''.join((c.lower() for c in text if c in valid_chars))
    return text.split()


def load_encoding():
    """Loads encoding from file."""

    path = PATH_TO_CORPUS + os.sep + 'encoding.npy'
    encoding = np.load(path)
    return encoding


def reload_encoding(max_dim=0, min_word_freq=0):
    """Recalculates encoding and saves it to file."""

    encoding = calculate_encoding(max_dim, min_word_freq)
    path = PATH_TO_CORPUS + os.sep + 'encoding.npy'
    np.save(path, encoding)
    return encoding

  
def calculate_encoding(max_dim=0, min_word_freq=0):
    """Generates a 1-of-N encoding from the corpus."""

    corpus_iter = get_corpus_iterrator(include_meta=False)
    # count words
    freq = Counter(chain(*corpus_iter))
    # filter small counts
    freq = [(i,w) for w,i in iter(freq.items()) if i>=min_word_freq]
    # trim dimension
    freq = sorted(freq, reverse=True)
    if max_dim: freq = freq[:max_dim]

    encoding = list(list(zip(*freq))[1])
    encoding.append('') # for unknown words
    return np.array(encoding)


def get_encode_function(encoding):
    """Returns a functions that encods a word to 1-of-N."""

    def encode(word):
        word = word.lower()
        if word is '':
            encoded = np.zeros(len(encoding))
        elif word in encoding:
            encoded = (encoding==word).astype(int)
        else : 
            encoded = (encoding=='').astype(int)
        return encoded

    return encode

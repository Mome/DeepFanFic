"""This module supplies a corpus document iterator and functions to handle 1-of-N encoding."""

from collections import Counter
from itertools import chain
import json
import os
import string

import numpy as np

PATH_TO_CORPUS = os.path.expanduser('~/deepfanfic_corpus')

def get_corpus_iterator(include_meta=True, **filter_options):
    """Itterates over the fanfiction corpus and returns documents represented as a list of words.

    Only acii letters are included in the list, also punctuation and digits are excluded."""

    for folder_name in os.listdir(PATH_TO_CORPUS):
        path = PATH_TO_CORPUS + '/' + folder_name
        story_path = path + '/stories'
        meta_path = path + '/meta'

        if not os.path.isdir(story_path):
            continue

        for doc_name in os.listdir(story_path):

            meta_name = doc_name.split('.')
            meta_name[-1] = 'json'
            meta_name.insert(1,'meta')
            meta_name = '.'.join(meta_name)
            try:
                with open(meta_path + '/' + meta_name) as f:
                    json_code = f.read()
                meta = json.loads(json_code)
            except Exception as e:
                print(e)
                meta = None

            if not meta is None:
                for opt_key, opt_value in filter_options.items():
                    if meta[opt_key] != opt_value:
                       skip = True
                       break
                else:
                    skip = False
            
            if skip: continue

            with open(story_path + '/' + doc_name) as f:
                text = f.read()

            word_list = to_machine_readable(text)

            if not include_meta:
                yield word_list
            else:
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

    corpus_iter = get_corpus_iterator(include_meta=False, language='English')
    # count words
    freq = Counter(chain(*corpus_iter))
    # filter small counts
    freq = [(i,w) for w,i in iter(freq.items()) if i>=min_word_freq]
    # trim dimension
    freq = sorted(freq, reverse=True)
    if max_dim: freq = freq[:max_dim]

    encoding = list(list(zip(*freq))[1])
    if '' not in encoding:
        encoding.append('') # for unknown words
    else:
        print('empty string already in encoding')
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


if __name__ == '__main__':
    for doc, meta in get_corpus_iterator(language='English'):
        print(len(doc), meta['language'])

    encoding = calculate_encoding(max_dim=10000, min_word_freq=5)
    encode = get_encode_function(encoding)
    print()
    print('the :', np.where(encode('the'))[0])
    print('hulk :', np.where(encode('hulk'))[0])
    print('harry :', np.where(encode('harry'))[0])
    print('moritz :', np.where(encode('moritz'))[0])
    print("''", np.where(encode('')))

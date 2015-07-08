"""This module supplies a corpus document iterator and functions to handle 1-of-N encoding."""

from collections import Counter
from itertools import chain
import json
import os
import string

import numpy as np

from utils import print_percent 


PATH_TO_CORPUS = os.path.expanduser('~/deepfanfic_corpus')
silent = True


def set_silent(b=None):
    global silent
    if b is None:
        silent = not silent
    else:
        silent = b


def count_documents():
    num_docs=0
    for folder_name in os.listdir(PATH_TO_CORPUS):
        story_path = PATH_TO_CORPUS + '/' + folder_name + '/stories'
        if os.path.isdir(story_path):
            num_docs += len(os.listdir(story_path))
    return num_docs


def get_corpus_iterator(include_meta=True, **filter_options):
    """Itterates over the fanfiction corpus and returns documents represented as a list of words.

    Only acii letters are included in the list, also punctuation and digits are excluded."""

    for folder_name in os.listdir(PATH_TO_CORPUS):
        path = PATH_TO_CORPUS + '/' + folder_name
        story_path = path + '/stories'
        meta_path = path + '/meta'

        if not silent:
            doc_num = count_documents()
            curr_num = 0

        if not os.path.isdir(story_path):
            continue

        for doc_name in os.listdir(story_path):
            
            if not silent:
                print_percent(curr_num/doc_num)
                curr_num+=1

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
    try:
        encoding = np.load(path)
    except:
        encoding = save_encoding()
    return encoding


def save_encoding(max_dim=0, min_word_freq=0, **filter_op   tions):
    """Recalculates encoding and saves it to file."""

    encoding = calculate_encoding(max_dim, min_word_freq, **filter_options)
    path = PATH_TO_CORPUS + os.sep + 'encoding.npy'
    np.save(path, encoding)
    return encoding

  
def calculate_encoding(max_dim=0, min_word_freq=0, **filter_options):
    """Generates a 1-of-N encoding from the corpus."""

    corpus_iter = get_corpus_iterator(include_meta=False, **filter_options)
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


def calculate_encoding2(max_dim=0, min_word_freq=0, **filter_options):
    """Generates a 1-of-N encoding from the corpus."""

    corpus_iter = get_corpus_iterator(include_meta=False, **filter_options)
    freq = Counter()
    for doc in corpus_iter:
        freq.update(doc)    
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


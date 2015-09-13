#!/bin/env python3
#
from qrnnlm import QRNNLM
from crawler import fanfic_crawler as fc
from utils import log
from time import sleep
import os

def main():
    path = os.path.expanduser("~/deepfanfic/demo")
    corpus_path = os.path.join(path, "corpus")

    if not os.path.exists(path):
        os.mkdir(path)

    """
    crawl fanfiction.net, create corpus
    path is specified in crawler file
    should match the aboce corpus_path
    """
    fnnc = fc.FFNCrawler(corpus_path)
    fnnc.start_crawling()
    print()
    print(' '*8,'## PRESS ENTER TO STOP CRAWLING! ##')
    print()
    try:
        input()
        print()
    finally:
        fnnc.stop_crawling()

    sleep(2)
    print()

    " crate the Query RNN Language Model object "
    qrnn = QRNNLM(path)

    " train a model for every file in corpus (saved in models_path) "
    qrnn.create_single_models(-1, True)

    " create index of vocabularies (saved in index_path, load with load_index()) "
    qrnn.create_index()

    " simple demo function to test models (interactive) "
    qrnn.test_models()

if __name__ == '__main__':
    main()

#!/bin/env python3
#
from qrnnlm import QRNNLM
from fanfiction_crawler import FanfictionCrawler
from corpus_reader import CorpusReader
from time import sleep
import os

''' Use the crawler first to get a number of documents '''

def main():
    path = os.path.expanduser("~/tmp/deep/demo")

    if not os.path.exists(path):
        os.makedirs(path)

    crawler = FanfictionCrawler(path=path, maxconnections=15, minsleeptime=0.5)
    crawler.crawl_random(amount=10)

    " crate the Query RNN Language Model object "
    qrnn = QRNNLM(path)
    """
    if the corpus does not reside in [path]/corpus, explicitly add the location:

        corpus_path = os.path.expanduser("~/deepfanfic_corpus")
        qrnn = QRNNLM(path, corpus_path)
    """

    " train a model for every file in the corpus "
    qrnn.create_single_models(-1, True)

    " create index of vocabulary for searching "
    qrnn.create_index()

    " simple demo function to test models (interactive) "
    qrnn.test_models()

if __name__ == '__main__':
    main()

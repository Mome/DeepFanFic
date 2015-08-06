#!/bin/env python3
#
from qrnnlm import QRNNLM
from crawler import fanfic_crawler as fc

def main():
    corpus_path = "~/deepfanfic_corpus"
    models_path = "~/deepfanfic_models"
    index_path = "~/deepfanfic_index"

    """
    crawl fanfiction.net, create corpus
    path is specified in crawler file
    should match the aboce corpus_path
    """
    fc.main()

    " crate the Query RNN Language Model object "
    qrnn = QRNNLM(corpus_path, models_path, index_path)

    " train a model for every file in corpus (saved in models_path) "
    qrnn.create_single_models()

    " create index of vocabularies (saved in index_path, load with load_index()) "
    qrnn.create_index()

    " simple demo function to test models (interactive) "
    qrnn.test_models()

#!/usr/bin/env python3
# encode: utf-8

import rnnlm as r
import corpus_reader as c
import numpy as np

filters = {'language' : 'english'}

n = 0
for [text,meta] in c.get_corpus_iterator(**filters):
    id = meta['storyid']

    voca = {"<s>":0, "</s>":1}
    vocalist = ["<s>", "</s>"]
    doc = []
    N = 0
    for w in text:
        if w not in voca:
            voca[w] = len(vocalist)
            vocalist.append(w)
        doc.append(voca[w])
    if len(doc) > 0:
        doc.append(1)

    print('id: %s' % id)
    #print('document:')
    #print(doc)

    V = len(vocalist) # input layer dimension
    K = 25 # hidden layer dimension
    I = 5 # epochs
    a = 1.0 # alpha, learning rate

    model = r.RNNLM_BPTT(V, K)
    for i in range(I):
        print(i,model.perplexity([doc]))
        model.learn([doc], a)
        a = a * 0.95 + 0.01
    print(I,model.perplexity([doc]))

    if n == 1:
        break
    n += 1

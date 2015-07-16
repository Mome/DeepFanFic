#!/usr/bin/env python3
# encode: utf-8

import os
import rnnlm as r
import corpus_reader as c

filters = {'language' : 'english'}

def  prepare_docs(texts):
    voca = {"<s>":0, "</s>":1}
    vocalist = ["<s>", "</s>"]
    docs = []
    for text in texts:
        doc = []
        for word in text:
            if word not in voca:
                voca[word] = len(vocalist)
                vocalist.append(word)
            doc.append(voca[word])
        if len(doc) > 0:
            doc.append(1) # end word
            docs.append(doc)
    return [len(vocalist), docs]
    

def main():
    count = 0
    max_count = 2 # number of documents to learn
    ids = []
    texts = []

    for [text,meta] in c.get_corpus_iterator(**filters):
        texts.append(text)
        ids.append(meta['storyid'])
        #print('\nid: %s' % id)
        count += 1
        if count == max_count:
            break
    train(5, 10, 1.0, ids, texts)

def train(I, K, a, ids, texts, path=''):
    '''
    I: number of epochs
    K: size of hidden layer
    a: learning rate alha
    ids: list of text ids for saving
    texts: list of texts to train on
    '''

    # train single document models
    for id, text in zip(ids, texts):
        [V, docs] = prepare_docs([text]) # V: input layer size

        model = r.RNNLM_BPTT(V, K)
        for i in range(I):
            print(i,model.perplexity(docs))
            model.learn(docs, a)
            a = a * 0.95 + 0.01
        print(I,model.perplexity(docs),'\n')

        if path != '':
            save(path, model, id)

def save(path, model, name):
    '''
    path: save location
    model: the model to save
    name: filename to save under
    '''
    with open(os.path.join(path,name), 'wb') as f:
        pickle.dump(model, f)

def load(path, name):
    '''
    path: location from  which to load
    name: name of the file
    '''
    with open(os.path.join(path,name), 'rb') as f:
        model = pickle.load(f)
    return model

#y = model.run([0])

if __name__ == '__main__':
    main()

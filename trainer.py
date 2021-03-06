#!/usr/bin/env python3
# encode: utf-8

import os
import rnnlm as r
import corpus_reader as c
import numpy as np
import pickle
import utils
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
np.seterr(over='ignore')

CORPUS_PATH = os.path.expanduser('~/deepfanfic_corpus/fanfiction.net/stories')
filters = {'language' : 'english'}

def prepare_docs(texts):
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
    return [vocalist, docs]
    
def main():
    path = os.path.expanduser('~/deepfanfic/models')
    create_single_models(-1, path, print_progress=True)
    #index = create_index(path)
    #save(path, index, 'index')
    #index = load(path, index, 'index')

def test_models(index, path):
    valid_models = query(['the'], index, path)
    vmodels = list(valid_models.items())
    vmodels.sort(key=lambda m : m[1], reverse=True)
    if len(vmodels) == 0 :
        print('No models found!')
        return
    bmodels = vmodels[:min(5,len(vmodels))]
    bmodels = [(id2name(idx), p) for idx,p in bmodels]
    for i,m in enumerate(bmodels):
        print(i+1, m[0].split('.')[2],'/t',m[1])

    i = input('press number of choice:')
    fname = bmodels[int(i)-1][0]
    path = os.path.join(CORPUS_PATH,fname)
    #with open(path,'w') as f:
    #    text = f.read()
    from subprocess import call
    call(['less',path])
    

def id2name(id):
    files = os.listdir(CORPUS_PATH)
    fname = [f for f in files if f.startswith('ffnet.'+str(id))][0]
    return fname

def query(query, index, path):
    names = set(index[query[0]])
    for word in query[1:]:
        names.intersection(index[word])

    model_probs = {}
    for name in names:
        [vlist,model] = load(path, name)
        dist = model.run([0])
        prob = 0
        for word in query:
            pos = vlist.index(word)
            prob += dist[pos]
        model_probs[name] = prob
    return model_probs

def create_index(path):
    index = {}
    modelfiles = os.listdir(path)
    for name in modelfiles:
        [vlist, _] = load(path, name)
        for w in vlist:
            if w not in index:
                index[w] = [name]
            else:
                index[w].append(name)
    return index

def create_single_models(max_count, path, print_progress=False):
    count = 0
    max_count = max(max_count, -1)
    doc_count = c.count_documents()
    if print_progress:
        print('Number of documents: %s' % str(doc_count))

    for [text,meta] in c.get_corpus_iterator(**filters):
        idx = meta['storyid']
        p = train_single(5, 10, 1.2, idx, text, path)
        if print_progress:
            print('Trained and saved model on document no %s/%s' % (str(count+1), str(doc_count)), end='\r')
            utils.print_percent(count/doc_count)
        #print('\nid: %s' % id)
        count += 1
        if count == max_count:
            break

    '''
    plt.figure(figsize=(20,15))
    legends = []
    for K in range(10,30,5):
        for a in [0.8,1.0,1.2]:
            p = train_singles(5, K, a, ids, texts)
            i, per = np.array(p).T
            plt.plot(i,per)
            legends.append(['K: '+str(K)+', a: '+str(a)])
    plt.legend(legends)
    plt.savefig('plots.svg')
    '''


def train_single(I, K, a, name, text, path=''):
    '''
    I: number of epochs
    K: size of hidden layer
    a: learning rate alha
    name: file/model name for saving
    text: text to train on
    '''

    perplexities = []
    # train single document model
    [vlist, docs] = prepare_docs([text])
    V = len(vlist) # input layer size

    model = r.RNNLM_BPTT(V, K)
    for i in range(I):
        perplexities.append([i,model.perplexity(docs)])
        model.learn(docs, a)
        a = a * 0.95 + 0.01
    perplexities.append([I,model.perplexity(docs)])

    if path != '':
        save(path, [vlist, model], name)
    return perplexities

def save(path, data, name):
    '''
    path: save location
    data: the model to save
    name: filename to save under
    '''
    with open(os.path.join(path,name), 'wb') as f:
        pickle.dump(data, f)
    f.close()

def load(path, name):
    '''
    path: location from  which to load
    name: name of the file
    '''
    with open(os.path.join(path,name), 'rb') as f:
        data = pickle.load(f)
    f.close()
    return data


if __name__ == '__main__':
    main()

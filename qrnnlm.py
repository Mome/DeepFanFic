#!/usr/bin/env python3
# encode: utf-8

import os
import rnnlm as r
import corpus_reader as CorpusReader
import numpy as np
import pickle
import utils
#import matplotlib
#matplotlib.use('agg')
#import matplotlib.pyplot as plt
np.seterr(over='ignore')

class QRNNLM():
    def __init__(self, path, corpus_path=''):
        self.base_path = os.path.expanduser(path)
        self.models_path = os.path.join(self.base_path, "models")
        if corpus_path == '':
            corpus_path = os.path.join(self.base_path, "corpus")
        self.corpus_path = corpus_path
        self.filters = {'language' : 'english'}
        self.cr = CorpusReader(corpus_path)


    def encode_docs(self, docs):
        """
        Encodes a list of documents into the necessary format for the RNN
        Returns a tuple of vocabulary and encoded documents
        texts :: list of documents to prepare
        """
        voc = {"<s>":0, "</s>":1} # mapping of words to encoding
        vlist = ["<s>", "</s>"] # vocabulary list
        edocs = [] # list of encoded documents
        for doc in docs:
            edoc = []
            for word in doc:
                if word not in voc:
                    voc[word] = len(vlist)
                    vlist.append(word)
                edoc.append(voc[word])
            if len(edoc) > 0:
                edoc.append(1) # end word
                edocs.append(edoc)
        return (vlist, edocs)
        

    def test_models(self):
        """
        Interactively test the trained models by entering query terms, shows best 5 matches
        """
        terms = input('Comma-separated list of query terms: ')
        termlist = [x.strip() for x in terms.split(',')]

        vmodels = list(self.query(termlist).items()) # find matching models
        vmodels.sort(key=lambda m : m[1], reverse=True) # sort
        if len(vmodels) == 0:
            print('No models found!')
            return

        bmodels = vmodels[:min(5,len(vmodels))] # best five or less
        bmodels = [(id2name(idx), p) for idx, p in bmodels] # get document paths

        for i, m in enumerate(bmodels): # show list of found models
            print(i+1, m[0].split('.')[2],'/t',m[1])

        i = input('Press number of choice: ')
        fname = bmodels[int(i)-1][0] # get chosen file name
        path = os.path.join(self.corpus_path, fname) # whole path

        with open(path, 'r') as f:
            print(f.read()) # show file content


    def id2name(self, idx):
        """
        Translates story/model id into file name of fan fiction document
        """
        files = os.listdir(self.corpus_path)
        fname = [f for f in files if f.startswith('ffnet.'+str(idx))][0]
        return fname


    def query(self, terms):
        """
        Query the trained models for terms
        Returns dictionary of terms and corresponding probability
        terms :: list of query terms
        """
        # find only documents containing all terms using the index
        ids = set(self.index[terms[0]])
        for term in terms[1:]:
            ids = ids.intersection(self.index[term])

        # calculate probabilites for words in these models
        model_probs = {}
        for idx in ids:
            vlist, model = self.load(path, idx)
            dist = model.run([0]) 
            prob = 0
            for term in terms:
                pos = vlist.index(term) # position of word in output vector
                prob += dist[pos] # use addition for now (else: smoothing and product)
            model_probs[term] = prob
        return model_probs


    def create_index(self):
        """
        Create index of terms and models they occur in
        """
        index = {}
        modelfiles = os.listdir(self.models_path)
        for name in modelfiles:
            if name != 'index':
                vlist,m = self.load(path, name)
                for w in vlist:
                    if w not in index:
                        index[w] = [name]
                    else:
                        index[w].append(name)
        self.index = index

    def create_single_models(self, max_count=-1, print_progress=False):
        count = 0
        max_count = max(max_count, -1)
        doc_count = self.cr.count_documents()
        if print_progress:
            print('Number of documents: %s' % str(doc_count))

        for [text,meta] in self.cr.get_corpus_iterator(**self.filters):
            idx = meta['storyid']
            p = self.train_single(5, 10, 1.2, idx, text)
            if print_progress:
                print('Trained and saved model on document no %s/%s' % (str(count+1), str(doc_count)), end='\r')
                utils.print_percent(count/doc_count)
            #print('\nid: %s' % id)
            count += 1
            if count >= max_count:
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


    def train_single(self, I, K, a, name, text):
        '''
        I: number of epochs
        K: size of hidden layer
        a: learning rate alha
        name: file/model name for saving
        text: text to train on
        '''

        perplexities = []
        # train single document model
        (vlist, docs) = self.encode_docs([text])
        print(vlist)
        V = len(vlist) # input layer size

        model = r.RNNLM_BPTT(V, K)
        for i in range(I):
            perplexities.append([i,model.perplexity(docs)])
            model.learn(docs, a)
            a = a * 0.95 + 0.01
        perplexities.append([I,model.perplexity(docs)])

        if self.models_path != '':
            self.save(self.models_path, [vlist, model], name)
        return perplexities

    def save(self, path, data, name):
        '''
        path: save location
        data: the model to save
        name: filename to save under
        '''
        with open(os.path.join(path,name), 'wb') as f:
            pickle.dump(data, f)
        f.close()

    def load(self, path, name):
        '''
        path: location from  which to load
        name: name of the file
        '''
        with open(os.path.join(path,name), 'rb') as f:
            data = pickle.load(f)
        f.close()
        return data


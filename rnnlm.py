#!/usr/bin/env python
# encode: utf-8

# Recurrent Neural Network Language Model
# This code is available under the MIT License.
# (c)2014 Nakatani Shuyo / Cybozu Labs Inc.

import numpy, codecs, re

class RNNLM:
    def __init__(self, V, K=10):
        self.K = K
        self.v = V
        self.U = numpy.random.randn(K, V) / 3
        self.W = numpy.random.randn(K, K) / 3
        self.V = numpy.random.randn(V, K) / 3

    def learn(self, docs, alpha=0.1):
        index = numpy.arange(len(docs))
        numpy.random.shuffle(index)
        for i in index:
            doc = docs[i]
            pre_s = numpy.zeros(self.K)
            pre_w = 0 # <s>
            for w in doc:
                s = 1 / (numpy.exp(- numpy.dot(self.W, pre_s) - self.U[:, pre_w]) + 1)
                z = numpy.dot(self.V, s)
                y = numpy.exp(z - z.max())
                y = y / y.sum()
                y[w] -= 1  # -e0
                eha = numpy.dot(y, self.V) * s * (s - 1) * alpha # eh * alpha
                self.V -= numpy.outer(y, s * alpha)
                self.U[:, pre_w] += eha
                self.W += numpy.outer(pre_s, eha)
                pre_w = w
                pre_s = s

    def perplexity(self, docs):
        log_like = 0
        N = 0
        for doc in docs:
            s = numpy.zeros(self.K)
            pre_w = 0 # <s>
            for w in doc:
                s = 1 / (numpy.exp(- numpy.dot(self.W, s) - self.U[:, pre_w]) + 1)
                z = numpy.dot(self.V, s)
                y = numpy.exp(z - z.max())
                y = y / y.sum()
                log_like -= numpy.log(y[w])
                pre_w = w
            N += len(doc)
        return log_like / N

    def dist(self, w):
        if w==0:
            self.s = numpy.zeros(self.K)
        else:
            self.s = 1 / (numpy.exp(- numpy.dot(self.W, self.s) - self.U[:, w]) + 1)
            z = numpy.dot(self.V, self.s)
            y = numpy.exp(z - z.max())
            return y / y.sum()

class RNNLM_BPTT(RNNLM):
    """RNNLM with BackPropagation Through Time"""
    def learn(self, docs, alpha=0.1, tau=3):
        index = numpy.arange(len(docs))
        numpy.random.shuffle(index)
        for i in index:
            doc = docs[i]
            pre_s = [numpy.zeros(self.K)]
            pre_w = [0] # <s>
            for w in doc:
                s = 1 / (numpy.exp(- numpy.dot(self.W, pre_s[-1]) - self.U[:, pre_w[-1]]) + 1)
                z = numpy.dot(self.V, s)
                y = numpy.exp(z - z.max())
                y = y / y.sum()

                # calculate errors
                y[w] -= 1  # -e0
                eh = [numpy.dot(y, self.V) * s * (s - 1)] # eh[t]
                for t in range(min(tau, len(pre_s)-1)):
                    st = pre_s[-1-t]
                    eh.append(numpy.dot(eh[-1], self.W) * st * (1 - st))

                # update parameters
                pre_w.append(w)
                pre_s.append(s)
                self.V -= numpy.outer(y, s * alpha)
                for t in range(len(eh)):
                    self.U[:, pre_w[-1-t]] += eh[t] * alpha
                    self.W += numpy.outer(pre_s[-2-t], eh[t]) * alpha

class BIGRAM:
    def __init__(self, V, alpha=0.01):
        self.V = V
        self.alpha = alpha
        self.count = dict()
        self.amount = numpy.zeros(V, dtype=int)
    def learn(self, docs):
        for doc in docs:
            pre_w = 0 # <s>
            for w in doc:
                if pre_w not in self.count:
                    self.count[pre_w] = {w:1}
                elif w not in self.count[pre_w]:
                    self.count[pre_w][w] = 1
                else:
                    self.count[pre_w][w] += 1
                self.amount[pre_w] += 1
                pre_w = w

    def perplexity(self, docs):
        log_like = 0
        N = 0
        va = self.V * self.alpha
        for doc in docs:
            pre_w = 0 # <s>
            for w in doc:
                c = 0
                if pre_w in self.count and w in self.count[pre_w]:
                    c = self.count[pre_w][w]
                log_like -= numpy.log((c + self.alpha) / (self.amount[pre_w] + va))
                pre_w = w
            N += len(doc)
        return log_like / N

def CorpusWrapper(corpus):
    for id in corpus.fileids():
        yield corpus.words(id)
'''
def main():
    numpy.random.seed(opt.seed)

    model = RNNLM_BPTT(V, K)
    a = 1.0
    I = 10
    for i in range(I):
        print i, model.perplexity(docs)
        model.learn(docs, a)
        a = a * 0.95 + 0.01
    print opt.I, model.perplexity(docs)

    if opt.output:
        import cPickle
        with open(opt.output, 'wb') as f:
            cPickle.dump([model, voca, vocalist], f)

    print ">> BIGRAM(alpha=%f)" % opt.alpha
    model = BIGRAM(V, opt.alpha)
    model.learn(docs)
    print model.perplexity(docs)
'''

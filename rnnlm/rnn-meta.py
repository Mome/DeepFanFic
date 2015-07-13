'''
Mostly a composite of:
https://github.com/mesnilgr/is13/blob/master/rnn/elman.py
http://deeplearning.net/tutorial/rnnslu.html
https://raw.githubusercontent.com/pascanur/DeepLearningBenchmarks/master/rnn/rnn.py
and now also: https://github.com/gwtaylor/theano-rnn/blob/master/rnn.py
'''

import theano
import theano.tensor as T
import time

import numpy
from collections import OrderedDict

class RNN(object):
    def __init__(self, input, words, hidden):
        '''
        x :: data
        words :: number of words / dimension of input
        hidden :: dimension of hidden layer
        '''

        floatX = theano.config.floatX

        # Initialize weights
        self.w_xh = theano.shared(0.2 * numpy.random.uniform(-1.0, 1.0 \
                                  (words, hidden)).astype(floatX))
        self.w_hh = theano.shared(0.2 * numpy.random.uniform(-1.0, 1.0 \
                                  (hidden, hidden)).astype(floatX))
        self.w_hy = theano.shared(0.2 * numpy.random.uniform(-1.0, 1.0 \
                                  (hidden, words)).astype(floatX))
        self.h0 = theano.shared(numpy.zeros(nh, dtype=floatX))

        self.params = [ self.w_xh, self.w_hh, self.w_hy ]
        self.names = [ 'w_xh', 'w_hh', 'w_hy' ]

        def recurrence(x_t, h_tm1):
            h_t = T.nnet.sigmoid(T.dot(x_t, self.w_xh) \
                                 + T.dot(h_tm1, self.w_hh))
            y_t = T.nnet.softmax(T.dot(h_t, self.w_hy))
            return [h_t, y_t]

        [self.h, self.y_g_x], _ = theano.scan(fn=recurrence, \
                                              sequences=self.input, \
                                              outputs_info=[self.h0, None])

        self.y_out = T.argmax(self.y_g_x, axis=-1)
        self.loss = lambda y: self.nll_multiclass(y)

        # shamelessly stolen from https://github.com/gwtaylor/theano-rnn/blob/master/rnn.py
        def nll_multiclass(self, y):
            # negative log likelihood based on multiclass cross entropy error
            # y.shape[0] is (symbolically) the number of rows in y, i.e.,
            # number of time steps (call it T) in the sequence
            # T.arange(y.shape[0]) is a symbolic vector which will contain
            # [0,1,2,... n-1] T.log(self.p_y_given_x) is a matrix of
            # Log-Probabilities (call it LP) with one row per example and
            # one column per class LP[T.arange(y.shape[0]),y] is a vector
            # v containing [LP[0,y[0]], LP[1,y[1]], LP[2,y[2]], ...,
            # LP[n-1,y[n-1]]] and T.mean(LP[T.arange(y.shape[0]),y]) is
            # the mean (across minibatch examples) of the elements in v,
            # i.e., the mean log-likelihood across the minibatch.
            return -T.mean(T.log(self.y_g_x)[T.arange(y.shape[0]), y])


class RNNLM(object):
    def __init__(self, words, hidden, learning_rate=0.01,
                     n_epochs=100, learning_rate_decay=1)
        self.x = T.matrix()
        self.y = T.vector(name='y', dtype='int32')
        self.h0 = T.vector('h0')
        self.lr = T.scalar('lr')
        self.rnn = RNN(self.x, self.words, self.hidden)
        
        self.predict_proba = theano.function(inputs=[self.x, ], \
                                             outputs=self.rnn.y_g_x)
        self.predict = theano.function(inputs=[self.x, ], \
                                       outputs=self.rnn.y_out)

    def fit(self, data):
        ''' How to get data in here?'''

        index = T.lscalar('index')        
        l_r = T.scalar('l_r', dtype=theano.config.floatX)
        cost = self.rnn.loss(self.y)

        compute_error = theano.function(inputs=[index, ], \
                                        outputs=self.rnn.loss(self.y), \
                                        givens={ \
                                            self.x: train_set_x[index], \
                                            self.y: train_set_y[index]})

        gradients = T.grad(cost, self.params)
        updates = OrderedDict((p, p-lr*g) for p, g in zip(self.params, gradients))
        print(updates)

        idxs = imatrix()
        self.train = theano.function(inputs=[idxs, t, lr], \
                                     outputs=costs, \
                                     updates=updates) 

        # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH!

if __name__ == '__main__':
    words = 6000
    a = numpy.zeros(words)
    a[0] = 1
    rnn = rnnlm(words, 25);
    for t in numpy.arange(100):
        numpy.random.shuffle(a)
        rnn.train(a, t, 0.1)

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


        l_r = T.scalar('l_r', dtype=floatX)
        cost = -T.mean(T.log(y, TT)

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

'''
Mostly a composite of:
https://github.com/mesnilgr/is13/blob/master/rnn/elman.py
http://deeplearning.net/tutorial/rnnslu.html
https://raw.githubusercontent.com/pascanur/DeepLearningBenchmarks/master/rnn/rnn.py
and now also: https://github.com/gwtaylor/theano-rnn/blob/master/rnn.py

TODO: * test if this does what it's supposed to (how?)
      * save trained model (and  possibility to load?)
'''

import theano
import theano.tensor as T
import time

import numpy
from collections import OrderedDict

class rnnlm(object):
    def __init__(self, words, hidden):
        '''
        words :: number of words / dimension of input
        hidden :: dimension of hidden layer
        '''

        floatX = theano.config.floatX

        # Initialize weights
        self.w_xh = theano.shared(0.2 * numpy.random.uniform(-1.0, 1.0, \
                                  (words, hidden)).astype(floatX))
        self.w_hh = theano.shared(0.2 * numpy.random.uniform(-1.0, 1.0, \
                                  (hidden, hidden)).astype(floatX))
        self.w_hy = theano.shared(0.2 * numpy.random.uniform(-1.0, 1.0, \
                                  (hidden, words)).astype(floatX))
        self.h0 = theano.shared(numpy.zeros(hidden, dtype=floatX))

        self.params = [ self.w_xh, self.w_hh, self.w_hy ]
        self.names = [ 'w_xh', 'w_hh', 'w_hy' ]

        x = T.imatrix()
        def recurrence(x_t, h_tm1):
            h_t = T.nnet.sigmoid(T.dot(x_t, self.w_xh) \
                                 + T.dot(h_tm1, self.w_hh))
            s_t = T.nnet.softmax(T.dot(h_t, self.w_hy))
            return [h_t, s_t]

        [h, y], _ = theano.scan(fn=recurrence, \
                                sequences=x, \
                                outputs_info=[self.h0, None])

        lr = T.scalar('l_r', dtype=floatX)
        cost = -T.mean(T.log(y))

        gradients = T.grad(cost, self.params)
        updates = OrderedDict((p, p-lr*g) for p, g in zip(self.params, gradients))

        self.train = theano.function(inputs=[x, lr], \
                                     outputs=cost, \
                                     updates=updates, \
                                     allow_input_downcast=True) 


if __name__ == '__main__':
    words = 6000
    steps = 100
    a = numpy.zeros(words)
    a[0] = 1
    b = numpy.zeros((steps,words))
    rnn = rnnlm(words, 25);
    for t in numpy.arange(steps):
        numpy.random.shuffle(a)
        b[t] = a
    theano.printing.Print("Params before training:", rnn.params)
    rnn.train(b, 0.001)
    theano.printing.Print("Params after training:", rnn.params)

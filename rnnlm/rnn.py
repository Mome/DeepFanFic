'''
Mostly a composite of:
https://github.com/mesnilgr/is13/blob/master/rnn/elman.py
http://deeplearning.net/tutorial/rnnslu.html
https://raw.githubusercontent.com/pascanur/DeepLearningBenchmarks/master/rnn/rnn.py
'''

import theano
import theano.tensor as T
import time

import numpy

class RNNLM(object):
    def __init__(self, n_w, n_h):
        '''
        n_w :: number of words / dimesions of input
        n_h :: dimension of hidden layer
        '''

        ''' Initial hidden input '''
        self.h0 = T.alloc(numpy.array(0, dtype=theano.config.floatX), n_h)

        ''' Random generator and floatX short-hand '''
        self.rng = numpy.random.RandomState(123534637)
        floatX = theano.config.floatX

        '''
        Initialize weights using normal distribution with
        standard deviation of 1/dimension
        '''
        w_xh = numpy.asarray(rng.normal(size=(n_w, n_h), \
                                        loc=0., \
                                        scale=1./n_w), \
                                        dtype=floatX)

        w_hh = numpy.asarray(rng.normal(size=(n_h, n_h), \
                                        loc=0., \
                                        scale=1./n_h), \
                                        dtype=floatX)

        w_hy = numpy.asarray(rng.normal(size=(n_h, n_w), \
                                        loc=0., \
                                        scale=1./n_h), \
                                        dtype=floatX)


        self.w_xh = theano.shared(w_xh, 'w_xh')
        self.w_hh = theano.shared(w_hh, 'w_hh')
        self.w_hy = theano.shared(w_hh, 'w_hy')

        t = T.ivector('t')
        _T = T.alloc(numpy.array(0, dtype=floatX), 100, n_w)
        arange = T.constant(numpy.arange(100).astype('int32'))
        ones = T.constant(numpy.ones((100,), dtype=floatX))
        TT = T.set_subtensor(_T[arange, t], ones)

        u = T.ivector('u')
        U = T.set_subtensor(_T[arange, u], ones)
        x = W_uh[u]

        def recurrence(x_t, h_tm1):
            h_t = T.nnet.sigmoid(T.dot(x_t, self.w_xh) \
                                 + T.dot(h_tm1, self.w_hh))
            s_t = T.nnet.softmax(T.dot(h_t, self.w_hy))
            return [h_t, s_t]

        [h, s], _ = theano.scan(fn=recurrence, \
                                sequences=x, \
                                outputs_info=[self.h0, None], \
                                n_steps=x.shape[0])

        cost = -TT.xlogx.xlogy0(TT, s[-1,0,:])
        cost = cost.sum(1).mean()
        updates = OrderedDict()

        grads = T.grad(cost, [self.w_hh, self.w_xh, self.w_hy])
        gw_hh, gw_xh, gw_hy = grads

        # Calculate weight updates
        updates[w_hh] = self.w_hh - lr*gw_hh
        updates[w_xh] = self.w_xh - lr*gw_xh
        updates[w_hy] = self.w_hy - lr*gw_hy

        self.train = theano.function(inputs=[x, t, lr], \
                                     outputs=cost, \
                                     name='train_step', \
                                     updates=updates) 

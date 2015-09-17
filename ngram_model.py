import nltk


class NgramModel():
    def __init__(self, word_list, n, voc_size, delta=0.0001):
        assert 1 < n < len(word_list)

        # ngram frequencies
        bgs = nltk.ngrams(word_list, n)
        self.n_fdist = nltk.FreqDist(bgs)

        # (n-1)-gram frequencies
        bgs = nltk.ngrams(word_list, n-1)
        self.nm_fdist = nltk.FreqDist(bgs)

        self.n = n
        self.voc_size = voc_size
        self.norm = (voc_size**n)*delta + word_list
        self.delta = delta


    def get_prob(self, words):
        prob = 1
        for ngram in nltk.ngrams(words, self.n):
            prob *= _get_prob(ngram)
        return prob


    def _get_prob(self, ngram):
        nar = self.n_fdist[ngram]+self.delta
        den = self.nm_fdist[ngram[:-1]]+self.delta*self.voc_size
        return nar/den


if __name__ == '__main__':
    max_i = 100
    ci = cr.get_corpus_iterator(yield_meta= False, language='german')
    print('counting ngrams:')
    for i,doc in enumerate(ci):
        doc_model = NgramModel(2, doc)
        counters.append(doc_model)        
        if max_i!=-1 and i>=max_i:
            break
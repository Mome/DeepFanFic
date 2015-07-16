import nltk


class NgramModel():
    def __init__(self, word_list, n, voc_size, default_value=0.0001):
        assert 1 < n < len(word_list)

        bgs = nltk.ngrams(word_list, n)
        self.n_fdist = nltk.FreqDist(bgs)

        bgs = nltk.ngrams(word_list, n-1)
        self.nm_fdist = nltk.FreqDist(bgs)

        self.n = n
        self.voc_size = voc_size
        self.norm = (voc_size**n)*default_value + word_list
        self.default_value


    def get_prob(self, words):
        prob = 1
        for ngram in nltk.ngrams(words, self.n):
            prob *= _get_prob(ngram)
        return prob


    def _get_prob(self, ngram):
        #assert len(ngram) == len(self.n)
        #count = self.fdist[ngram]
        #return (count+self.default_value)/self.norm
        return self.n_fdist[ngram]/self.nm_fdist[ngram[:-1]]


if __name__ == '__main__':
    max_i = 100
    ci = cr.get_corpus_iterator(yield_meta= False, language='german')
    print('counting ngrams:')
    for i,doc in enumerate(ci):
        doc_model = NgramModel(2, doc)
        counters.append(doc_model)        
        if max_i!=-1 and i>=max_i:
            break
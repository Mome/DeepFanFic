from corpus_reader import *

from memory_profiler import profile

ci = get_corpus_iterator(language='german')

@profile
def next():
    n = ci.next()
    print(len(n[0]),len(n[1]))


while True:
    try:
        next()
    except:
        break
print('ende')

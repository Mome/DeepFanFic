from fff_interface import do_download
from random import randint
import os
import threading

CORPUS_FOLDER = os.path.expanduser('~/deepfanfic_corpus')

sites = [
    ('fanfiction.net', 'http://www.fanfiction.net/s/', 11330930),
]

numbers = list(zip(*sites))[2]
abs_number = sum(numbers)

def get_random_url():

    r = randint(1,abs_number)

    cumsum = 0
    for name, crawl_url, max_num in sites:
        cumsum += max_num
        if cumsum <= r:
            break
    
    url = crawl_url + str(r-cumsum+max_num)

    return url, CORPUS_FOLDER + '/' + name


def start_crawling(max_iterations):
    global stop
    stop=False
    threading.Thread(
        target=download,
        args=(max_iterations,),
    ).start()


def download(max_iterations):
    print 'iterations', max_iterations, stop
    for i in range(max_iterations):
        print i,',',
        url, path = get_random_url()
        try:
            do_download(url, path)
        except:
            pass
        if stop: break
    print 'finished !!!'

stop = True

import sys
max_it = sys.argv[1]

start_crawling(int(max_it))
print
#print(' '*8,'###################################')
print ' '*8,'## PRESS ENTER TO STOP CRAWLING! ##'
#print(' '*8,'###################################')
print
try:
    raw_input()
    print '## Sending manual Stop Signal ##'
    print
finally:
    stop = True


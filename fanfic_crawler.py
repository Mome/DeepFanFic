#! /usr/bin/python3
from __future__ import print_function
from __future__ import division

from datetime import datetime
from itertools import count
import os
from random import random
import subprocess
import sys
import threading
from time import time, sleep


from utils import which, eprint, rand_perm

if sys.version_info < (3,0):
    input = raw_input
if sys.version_info < (3,3):
    DEVNULL = open(os.devnull, "w")
else:
    DEVNULL = subprocess.DEVNULL

if not which('fanficfare'):
    raise UserWarning(
        """No fanficfare found, use:
           pip install git+https://github.com/JimmXinu/FanFicFare"""
    )


default_folder = os.path.expanduser('~/deepfanfic_corpus')
if not os.path.exists(default_folder): os.makedirs(default_folder)

# logging
log_file = open(default_folder+'/crawler_log','a')
def log(message):
    t = time()
    timestamp = datetime.fromtimestamp(t).strftime('%H:%M:%S')
    message = timestamp + ' ' + str(message)
    log_file.write(message + '\n')
    log_file.flush()
    eprint(message)
    return t

class FFNCrawler:
    """fanfiction.net crawler"""

    domain = 'http://www.fanfiction.net'
    just_in_all = '/j/0/0/0'
    just_in_stories_new = '/j/0/1/0'
    just_in_stories_up = '/j/0/2/0'
    just_in_cross_new = '/j/0/3/0'
    just_in_cross_up = '/j/0/4/0'
    super_categories = {'stories', 'crossover'}
    categories = {'anime', 'books', 'cartons', 'comics', 'games',
        'misc', 'plays', 'movies', 'tv'}

    def __init__(self, folder=None):
        if folder is None:
            folder = default_folder
        folder = folder + '/fanfiction.net'

        story_folder =  folder + '/stories'
        meta_folder =  folder + '/meta'

        if not os.path.exists(story_folder): os.makedirs(story_folder)
        if not os.path.exists(meta_folder): os.makedirs(meta_folder)

        self.fffw = FFFWrapper(story_folder, meta_folder)

        self.stop = True

        self.folder = folder
        self.story_folder = story_folder
        self.meta_folder = meta_folder

    def start_crawling(self, start_id=None, end_id=None,max_iterations=None):
        threading.Thread(
            target=self.run_crawer,
            args=(start_id, end_id, max_iterations),
        ).start()

    def run_crawer(self, start_id=None, end_id=None, max_iterations=None, parallel=False):

        sleep(1)

        if end_id is None: end_id = float('inf')
        if max_iterations is None: max_iterations = float('inf')

        max_parallel = 20
        if parallel and max_iterations > max_parallel:
            raise ValueError("I won't allow a parralel crawl with more than " \
                + str(max_parallel) + " queries. Set max_iterations to a smaller value!!")


        if not self.stop:
            raise Exeption('Already crawling!')
        self.stop = False

        filename = self.folder + '/last_id'
        try:
            if start_id is None:
                if os.path.exists(filename):
                    with open(filename) as f:
                        last_id = int(f.read())
                        story_id = last_id+1
                else:
                    log('Last_id file not found!')
                    story_id = 0
            else:
                story_id = start_id
        except Exception as e:
            self.stop = True
            raise e

        query_store = []
        try:
            for iteration in count():
                st = log('Download story_id: ' + str(story_id)) 

                story_query = self.download_story(story_id)
                #meta_query = self.download_metadata(story_id)

                if parallel:
                    query_store += [story_query]#, meta_query]
                else:
                    story_query.wait()
                    #meta_query.wait()
                    log_file.flush()
                    sleep(max(0,0.5-time()+st)) # if query was too short sleep a little while
                    #sleep(random()/10)

                story_id+=1
                
                if iteration >= max_iterations or story_id >= end_id:
                    self.stop = True
                if self.stop:
                    break

        except Exception as e:
            log(repr(e) + ' ' + str(e))
            raise e
        finally:
            with open(filename, 'w') as f:
                f.write(str(story_id-1))
            if parallel:
                for q in query_store:
                    q.wait()
            self.stop = True
            log('finished')
            
    def stop_crawling(self):
        self.stop = True

    def download_metadata(self, story_id):
        url = FFNCrawler.domain + '/s/' + str(story_id)
        return self.fffw.download_metadata(url)

    def download_story(self, story_id):
        url = FFNCrawler.domain + '/s/' + str(story_id)
        return self.fffw.download_story(url)

    @staticmethod
    def list_new():
        url = FFNCrawler.domain + FFNCrawler.just_in_all
        return FFFWrapper.list_story_urls(url)

    @staticmethod
    def map_id(id_):
        if id_<= 100000:
            return id_
        prime = 11213519
        trans_id = rand_perm(id_-100000, prime)
        return trans_id + 100000



class FFFWrapper:
    """fanficfare wrapper""" 

    def __init__(self, story_cwd, meta_cwd):
        # execution folders
        self.story_cwd = story_cwd
        self.meta_cwd = meta_cwd

    def download_metadata(self, url):
        return self.call_fff(url, self.meta_cwd, '-m')

    def download_story(self, url):
        return self.call_fff(url, self.story_cwd)

    @staticmethod
    def get_url_examples(self):
        args = ['fanficfare', '--format=txt', '-s', url]
        out = subprocess.check_output(
            args=args,
            universal_newlines=True,
        )
        return out.split('\n')

    @staticmethod
    def list_story_urls(url, normalized=True):
        list_arg = '-n' if normalized else '-l'
        args = ['fanficfare','--format=txt', list_arg, url]
        out = subprocess.check_output(
            args=args,
            universal_newlines=True,
        )
        return out.split('\n')

    @staticmethod
    def call_fff(url, cwd=None, args=''):
        if isinstance(args, str):
            args = args.split()
        args = ['fanficfare','--format=txt'] + args + [url]
        return subprocess.Popen(args, cwd=cwd, stdout=DEVNULL, stderr=log_file)

def extrac_all_metadata(story_folder, meta_folder):
    for d in story_folder.listdir():
        extract_metadata(file_path, meta_folder)

def extract_metadata(file_path, meta_folder):
    # insert underscores
    # put number to the front
    # check for corresponding filename in metadata
    # create metafile
    pass

def main():
    
    if len(sys.argv) > 1:
        start = sys.argv[1]
        if start.lower() in ['none','no','last']:
            start = None
        else:
            start = int(start)
    else: 
        start = None
    if len(sys.argv) > 2:
        end = sys.argv[2]
        if end.lower() in ['none','no']:
            end = None
        else:
            end = int(end)    
    else:
        end = None
    if len(sys.argv) > 3:
        max_it = sys.argv[3]
        if max_it.lower() in ['no','none']:
            max_it = None
        else:
            max_it = int(max_it)
    else:
        max_it = None

    log('Start non parallel crawling on fanfiction.net')
    fnnc = FFNCrawler()
    fnnc.start_crawling(start,end,max_it)
    print()
    #print(' '*8,'###################################')
    print(' '*8,'## PRESS ENTER TO STOP CRAWLING! ##')
    #print(' '*8,'###################################')
    print()
    try:
        input()
        log('## Sending manual Stop Signal ##')
        print()
    finally:
        fnnc.stop_crawling()
    
if __name__ == '__main__':
    main()

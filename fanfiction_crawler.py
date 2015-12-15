#! /usr/bin/python3
from urllib.parse import quote_plus, urlsplit
import subprocess
from functools import partial
from itertools import count
import threading
import os
import uuid
import json
import random
import time
import queue

from utils import is_int, rlinput

DEFAULT_PATH = '~/deepfanfic/demo/corpus/fanfiction.net'
MAXCONNECTIONS = 10
SLEEPTIME = 1.5

domain = 'http://www.fanfiction.net'

categories = {
    'Lord-of-the-Rings' : ['book', 382],
    'Greek-Mythology' : ['misc', 1366],
    'Indiana-Jones' : ['movie', 177],
    'Harry-Potter' : ['book', 224],
    'South-Park' : ['cartoon', 5],
    'Star-Wars'  : ['movie', 8],
    'Half-Life' : ['game', 599],
    'Doctor-Who' : ['tv', 21],
    'Batman' : ['comic', 50],
    'Pokemon' : ['game', 80],
}

personal_config = """
[defaults]
is_adult:true
# output_filename: ${title}-${siteabbrev}_${storyId}${formatext}
output_filename: ${siteabbrev}_${storyId}${formatext}
include_titlepage: false
include_tocpage: false

[txt]
windows_eol: false
wrap_width: 0
titlepage_entries:

file_start:

file_end:

"""


def get_search_url(keywords, page):

    keywords = [k.lower() for k in keywords.split() if k]
    keywords = ' '.join(keywords)
    keywords = quote_plus(keywords)

    search_template = (domain + 
        '/search.php?ready=1&keywords='
        '{keywords}'
        '&type=story&ppage='
        '{page}')
    
    url = search_template.format(keywords=keywords, page=page)
    return url


def get_story_url(topic, page):
    category = categories[topic][0]
    page = '?p='+str(page)
    url = '/'.join([domain, category, topic, page])
    return url


def get_crossover_url(topic1, topic2, page):
    id1  = categories[topic1][1]
    id2  = categories[topic2][1]
    return '/'.join([
        domain,
        topic1 + '-and-' + topic2 + '-Crossovers',
        str(id1), str(id2),
        '?p='+str(page) ])


def get_latest_story_id():
    url = 'http://www.fanfiction.net/j/0/0/0'
    devnull = open(os.devnull)
    links = extract_links(url, stderr=devnull)
    story_ids = [l.split('://', 1)[-1].split('/')[2] for l in links if l.strip()]
    #print(story_ids)
    story_ids = [int(sid) for sid in story_ids if is_int(sid)]
    return max(story_ids)


def extract_links(url, stderr=None):
    cmd = ['fanficfare', '-l', url]
    try:
        out = subprocess.check_output(cmd, stderr=stderr)
        links = out.decode().strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(e)
        links = []

    links = list(filter(bool, links))

    if not links:
        print('Could not extract links!')
    return links


def link_extractor(get_url, amount, start_page=1, stderr=None):
    link_count = 0
    for page in count(start_page):
        url = get_url(page=page)
        print('Extract links from:', url)

        link_list = extract_links(url, stderr=stderr)

        if not link_list:
            break

        for link in link_list:
            yield link
            link_count += 1
            if link_count >= amount:
                return


def random_links_generator(amount):
    print('Get latest story id...')
    max_sid = get_latest_story_id()
    print('max_id = ', max_sid)

    if amount is None or amount > max_sid:
        amount = max_sid

    for id_ in random.sample(range(max_sid), amount):
        yield '/'.join([domain, 's', str(id_)])


def search_links(keywords, page_number, start_page=0):
    keywords = quote_plus(keywords)
    links = []
    for i in range(start_page, start_page+page_number):
        search_str = search_template.format(keywords=keywords, page=i)
        cmd = ['fanficfare', '-l', search_str]
        out = subprocess.check_output(cmd)
        links += out.decode().strip().split('\n')
    return links


def transform_title(title):
    title = title.lower()
    title = title.replace('_',' ')
    title = title.replace('.',' ')
    title = '_'.join([c.strip() for c in title.split()])
    return title


class FanfictionCrawler:
    def __init__(self, path, maxconnections=MAXCONNECTIONS):
        self.path = path
        self.maxconnections = maxconnections

        # create configuration file in /tmp
        config_path = str(uuid.uuid4()) + '_personal.ini'
        config_path = os.path.join('/tmp', config_path)
        open(config_path, 'w').write(personal_config)

        self.config_path = config_path
        self.logfile = open('crawler.log', 'a')

    def crawl_random(self, amount):
        links = random_links_generator(amount)
        print()
        self.crawl(links)

    def crawl_by_search(self, keywords, amount):
        get_url = partial(get_search_url, keywords=keywords)
        links = link_extractor(get_url, amount)
        self.crawl(links)

    def crawl_stories(self, topic, amount):
        get_url = partial(get_story_url, topic=topic)
        links = link_extractor(get_url, amount)
        self.crawl(links)

    def crawl_crossover(self, topic1, topic2, amount):
        get_url = partial(get_crossover_url, topic1=topic1, topic2=topic2)
        links = link_extractor(get_url, amount)
        self.crawl(links)

    def crawl(self, links):
        q = queue.Queue(MAXCONNECTIONS*2)

        def download_wrapper():
            while True:
                url = q.get()
                print('Download:', url)
                try:
                    self.download(
                        url = url,
                        stdout = self.logfile,
                        stderr = self.logfile,
                    )
                except CrawlingException as ce:
                    print('CrawlingException:', url, ':', ce)
                finally:
                    q.task_done()
                    print('DONE:', url)

        threads = []
        for _ in range(MAXCONNECTIONS):
            t = threading.Thread(target=download_wrapper)
            t.daemon = True
            t.start()

        timestamp = 0
        
        # put a new url in the queue after `SLEEPTIME` seconds
        for url in links:
            diff = time.time() - timestamp
            if diff < SLEEPTIME:
                time.sleep(SLEEPTIME-diff)
            timestamp = time.time()

            q.put(url)

        print('wait for tasks to be done')
        q.join()
        print('all tasks done')
        

    def download(self, url, stdout=None, stderr=None):

        # get story ID and title
        url_parts = url.split('://')[-1].split('/')
        story_id = url_parts[2]
        try:
            title = transform_title(url_parts[4])
        except:
            pass

        # cosntruct directories
        story_path = os.path.join(self.path, 'stories')
        meta_path = os.path.join(self.path, 'meta')
        os.makedirs(story_path, exist_ok=True)
        os.makedirs(meta_path, exist_ok=True)

        # download meta
        cmd = ['fanficfare', '-f', 'txt', '-c', self.config_path, '-m', url]
        try:
            out = subprocess.check_output(cmd, stderr=stderr, cwd=self.path).decode()

            if out.startswith('Story does not exist'):
                raise CrawlingException('Story does not exist!')

            # reconvert string representation of dict and json code
            meta_dict = eval(out)
            json_code = json.dumps(meta_dict)

            try:
                title = transform_title(meta_dict['title'])
            except:
                title = transform_title(uuid())

            filename = ['ffnet', 'meta', story_id, title, 'json']
            filename = '.'.join(filename)

            with open(os.path.join(meta_path, filename), 'w') as f:
                f.write(json_code)

        except subprocess.CalledProcessError as e:
            print('Could not acquire metadata:', e)

        if 'title' not in locals():
            title = transform_title(uuid())

        old_file_name = 'ffnet_' + story_id + '.txt'
        new_file_name = 'ffnet_' + story_id + '_' + title + '.txt'

        if os.path.exists(os.path.join(self.path, old_file_name)):
            os.remove(os.path.join(self.path, old_file_name))

        # download story
        try:
            cmd = ['fanficfare', '-c', self.config_path, '-f', 'txt',  url]
            print(cmd)
            subprocess.call(cmd, cwd=story_path, stdout=stdout, stderr=stderr)

            # rename the story file
            old_name = 'ffnet_' + story_id + '.txt'
            new_name = 'ffnet_' + story_id + '_' + title + '.txt'
            os.rename(os.path.join(story_path, old_file_name), os.path.join(story_path, new_file_name))

        except Exception as e:
            print('Could not acquire story:', e)


class CrawlingException(Exception):
    pass


def pick_topic(det='a'):
    
    topics = list(categories.keys())
    
    print('Pick %s topic:' % det)
    for i,top in enumerate(topics, start=1):
        print('  ' + str(i) + ' - ' + top.replace('-',' '))
    
    while True:
        index = input('Enter number between 1 and %s: ' % len(topics))
        index = int(index)-1
        if index in range(len(topics)):
            break

    return topics[index]


def crawl_dialog():

    # number of stories to be crawled
    link_amount = None
    while not link_amount:   
        mes = 'Amount of stories to crawl (empty for infinite): '
        link_amount = input(mes).strip()

        if not link_amount:
            link_amount = float('inf')
        else:
            try:
                link_amount = int(link_amount)
            except:
                link_amount = -1

            if link_amount <= 0:
                link_amount = None

    # storage path
    path = rlinput('Storage path: ', DEFAULT_PATH)
    path = os.path.expanduser(path)

    # choose download mode
    print()
    print('How do you want to crawl ?')
    print('  1 - Story\n  2 - Crossover\n  3 - Free Search\n  4 - Random Stories')
    mode = None
    while not mode:
        mode = input('Enter number: ').strip()
        if mode == '1':
            mode = 'story'
        elif mode == '2':
            mode = 'crossover'
        elif mode == '3':
            mode = 'search'
        elif mode == '4':
            mode = 'random'
        else:
            mode = None

    #create crawler
    crawler = FanfictionCrawler(path)

    if mode == 'story':
        topic = pick_topic()
        print()
        crawler.crawl_stories(topic, link_amount)

    if mode == 'crossover':
        topic1 = pick_topic('first')
        print()
        topic2 = pick_topic('second')
        print()
        crawler.crawl_crossover(topic1, topic2, link_amount)
    
    if mode == 'search':
        keywords = input('Enter search term: ')
        crawler.crawl_by_search(keywords, link_amount)

    if mode == 'random':
        crawler.crawl_random(link_amount)

    print()


if __name__ == '__main__':
    crawl_dialog()

#! /usr/bin/python3
from urllib.parse import quote_plus, urlsplit
import subprocess
from pprint import pprint
from functools import partial
from itertools import count
import threading
import os
import uuid
import json
import atexit

PATH = '~/deepfanfic/demo/corpus/fanfiction.net'

maxconnections = 10

domain = 'http://www.fanfiction.net'

categories = {
    'Harry-Potter' : ['book', 224],
    'Lord-of-the-Rings' : ['book', 382],
    'Doctor-Who' : ['tv', 21],
    'Indiana-Jones' : ['movie', 177],
    'South-Park' : ['cartoon', 5],
    'Star-Wars'  : ['movie', 8],
    'Pokemon' : ['game', 80],
    'Half-Life' : ['game', 599],
    'Greek-Mythology' : ['misc', 1366],
    'Batman' : ['comic',50],
}

personal = """
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

def search_links(keywords, page_number, start_page=0):
    keywords = quote_plus(keywords)
    links = []
    for i in range(start_page, start_page+page_number):
        search_str = search_template.format(keywords=keywords, page=i)
        cmd = ['fanficfare', '-l', search_str]
        out = subprocess.check_output(cmd)
        links += out.decode().strip().split('\n')
    return links


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


def link_generator(get_url, start_page=1, stderr=None):
    for page in count(start_page):
        url = get_url(page=page)
        print('Extract links from:', url)

        link_list = extract_links(url, stderr=stderr)

        if not link_list:
            break

        for link in link_list:
            yield link


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


def download(url, path, config_path, stdout=None, stderr=None, pool=None):

    # get story ID and title
    url_parts = url.split('://')[-1].split('/')
    story_id = url_parts[2]
    title = transform_title(url_parts[4])

    # cosntruct directories
    story_path = os.path.join(path, 'stories')
    meta_path = os.path.join(path, 'meta')
    os.makedirs(story_path, exist_ok=True)
    os.makedirs(meta_path, exist_ok=True)

    # download story
    cmd = ['fanficfare','-c', config_path, '-f', 'txt',  url]
    subprocess.call(cmd, cwd=story_path, stdout=stdout, stderr=stderr)

    # download meta
    cmd = ['fanficfare', '-f', 'txt', '-c', config_path, '-m', url]
    try:
        out = subprocess.check_output(cmd, stderr=stderr, cwd=story_path).decode()

        # reconvert string representatio of dict and json code
        meta_dict = eval(out)
        json_code = json.dumps(meta_dict)

        # create filename
        filename = ['ffnet', 'meta', story_id, title, 'json']
        filename = '.'.join(filename)

        with open(os.path.join(meta_path, filename), 'w') as f:
            f.write(json_code)
    except subprocess.CalledProcessError as e:
        print('Could not acquire metadata:', e)

    # rename the story file
    old_name = 'ffnet_' + story_id + '.txt'
    new_name = 'ffnet_' + story_id + '_' + title + '.txt'
    os.rename(os.path.join(story_path, old_name), os.path.join(story_path, new_name))

    if pool:
        pool.release()

def transform_title(title):
    title = title.lower()
    title = title.replace('_',' ')
    title = title.replace('.',' ')
    title = '_'.join([c.strip() for c in title.split()])
    return title

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



if __name__ == '__main__':

    path = os.path.expanduser(PATH)

    # create temporal configuration file
    config_path = str(uuid.uuid4()) + '_personal.ini'
    config_path = os.path.join('/tmp', config_path)
    open(config_path, 'w').write(personal)

    print()
    print('How do you want to crawl ?')
    print('  1 - Story\n  2 - Crossover\n  3 - Free Search')

    mode = None
    while not mode:   
        mode = input('Enter number: ').strip()
        if mode == '1':
            mode = 'story'
        elif mode == '2':
            mode = 'crossover'
        elif mode == '3':
            mode = 'search'
        else:
            mode = None
    print()

    if mode == 'story':
        topic = pick_topic()
        get_url = partial(get_story_url, topic=topic)

    if mode == 'crossover':
        topic1 = pick_topic(' first ')
        topic2 = pick_topic(' second ')
        get_url = partial(get_crossover_url, topic1=topic1, topic2=topic2)
    
    if mode == 'search':
        keywords = input('Enter search term: ')
        get_url = partial(get_search_url, keywords=keywords)

    print()

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

    logfile = open('crawler.log','a')
    pool = threading.BoundedSemaphore(maxconnections)

    for url in link_generator(get_url, stderr=logfile):
        if link_amount <= 0:
            break

        pool.acquire()

        print('Download:', url)

        threading.Thread(
            target=download,
            kwargs={
                'url' : url,
                'path' : path, 
                'config_path' : config_path,
                'stdout' : logfile,
                'stderr' : logfile,
                'pool' : pool,
            }
        ).start()

        link_amount -= 1

    atexit.register(os.remove, config_path)

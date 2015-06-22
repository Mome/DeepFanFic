from collections import namedtuple
from os.path import expanduser, isfile, join, dirname
from os import access, R_OK
from subprocess import call
import ConfigParser
import getpass
import logging
import pprint
import string
import sys

if sys.version_info < (2, 5):
    print 'This program requires Python 2.5 or newer.'
    sys.exit(1)

if sys.version_info >= (2, 7):
    # suppresses default logger.  Logging is setup in fanficdownload/__init__.py so it works in calibre, too.
    rootlogger = logging.getLogger()
    loghandler = logging.NullHandler()
    loghandler.setFormatter(logging.Formatter('(=====)(levelname)s:%(message)s'))
    rootlogger.addHandler(loghandler)


from fanficfare import adapters, exceptions
from fanficfare.configurable import Configuration
from fanficfare.epubutils import get_dcsource_chaptercount, get_update_data
from fanficfare.geturls import get_urls_from_page

from text_writer import TextWriter

def download(url):
    story_path = expanduser('~/deepfanfic_corpus/fanfiction.net/stories')
    meta_path = expanduser('~/deepfanfic_corpus/fanfiction.net/meta')
    do_download(url,story_path,meta_path)

def write_story(config, adapter, writeformat, metaonly=False, outstream=None, story_path=None):
    #writer = writers.getWriter(writeformat, config, adapter)
    writer = TextWriter(config, adapter)
    writer.writeStory(outstream=outstream, metaonly=metaonly, outpath=story_path)
    output_filename = writer.getOutputFileName()
    del writer
    return output_filename.split('/')[-1]

def do_download(url,corpus_path):

    story_path = corpus_path + '/stories'
    meta_path = corpus_path + '/meta'

    options = {
        'format' : 'txt',
        'configfile' : False,
        'list' : False,
        'normalize' : False,
        'force' : False,
        'options' : [],
        'metaonly' : False,
    }
    options = namedtuple('Options', options.keys())(**options)
        
    output_filename = None
    
    # create configuration        
    try:
        configuration = Configuration(adapters.getConfigSectionFor(url), options.format)
    except exceptions.UnknownSite, e:
        if options.list or options.normalize:
            # list for page doesn't have to be a supported site.
            configuration = Configuration('test1.com', options.format)
        else:
            raise e

    conflist = []
    if isfile(join(dirname(__file__), 'defaults.ini')):
        conflist.append(join(dirname(__file__), 'defaults.ini'))
    if isfile('defaults.ini'):
        conflist.append('defaults.ini')
    if isfile(join(dirname(__file__), 'personal.ini')):
        conflist.append(join(dirname(__file__), 'personal.ini'))
    if isfile('personal.ini'):
        conflist.append('personal.ini')

    if options.configfile:
        conflist.extend(options.configfile)

    logging.debug('reading %s config file(s), if present' % conflist)
    configuration.read(conflist)

    try:
        configuration.add_section('overrides')
    except ConfigParser.DuplicateSectionError:
        pass

    if options.force:
        configuration.set('overrides', 'always_overwrite', 'true')

    if options.options:
        for opt in options.options:
            (var, val) = opt.split('=')
            configuration.set('overrides', var, val)

    if options.list or options.normalize:
        retlist = get_urls_from_page(url, configuration, normalize=options.normalize)
        return '\n'.join(retlist)
        

    try:
        adapter = adapters.getAdapter(configuration, url)
        #adapter.setChaptersRange(options.begin, options.end)

        # three tries, that's enough if both user/pass & is_adult needed,
        # or a couple tries of one or the other
        for x in range(0, 2):
            try:
                adapter.getStoryMetadataOnly()
            except exceptions.FailedToLogin, f:
                if f.passwdonly:
                    print 'Story requires a password.'
                else:
                    print 'Login Failed, Need Username/Password.'
                    sys.stdout.write('Username: ')
                    adapter.username = sys.stdin.readline().strip()
                adapter.password = getpass.getpass(prompt='Password: ')
                # print('Login: `%s`, Password: `%s`' % (adapter.username, adapter.password))
            except exceptions.AdultCheckRequired:
                print 'Please confirm you are an adult in your locale: (y/n)?'
                if sys.stdin.readline().strip().lower().startswith('y'):
                    adapter.is_adult = True

        # regular download
        if options.metaonly:
            pprint.pprint(adapter.getStoryMetadataOnly().getAllMetadata())
        
        shall_write = True
        if shall_write:
            output_filename = write_story(configuration, adapter, options.format, options.metaonly, story_path=story_path)

            # store metadata separately  
            #from time import time
            #time_0 = time()
            meta_dict = adapter.getStoryMetadataOnly().getAllMetadata()
            import json
            json_dump = json.dumps(meta_dict,sort_keys=True,indent=0)
            meta_filename = change_filename(output_filename,meta=True)
            import os
            meta_path = os.path.expanduser('~/deepfanfic_corpus/fanfiction.net/meta') + '/' + meta_filename

            with open(meta_path, 'w') as f:
                f.write(json_dump) 
            #print 'time', time()-time_0
            #time_0 = time()

        """text = []
        for index, (url, title, html) in enumerate(adapter.getChapters()):
            if html:
                vals={'url':url, 'chapter':title, 'index':"%04d"%(index+1), 'number':index+1}
                #self._write(out,self.lineends(self.wraplines(removeAllEntities(CHAPTER_START.substitute(vals)))))
                text.append(html2text(html))#,wrap_width=self.wrap_width)
                #self._write(out,self.lineends(self.wraplines(removeAllEntities(CHAPTER_END.substitute(vals)))))
        '\n'.join(text)"""


        if not options.metaonly and adapter.getConfig('post_process_cmd'):
            metadata = adapter.story.metadata
            metadata['output_filename'] = output_filename
            call(string.Template(adapter.getConfig('post_process_cmd')).substitute(metadata), shell=True)

        del adapter

    except exceptions.InvalidStoryURL, isu:
        print isu
    except exceptions.StoryDoesNotExist, dne:
        print dne
    except exceptions.UnknownSite, us:
        print us

def change_filename(filename, meta=False):
    import re
    assert filename.endswith('.txt')
    uindex = len(filename) - filename.rindex('_')
    tup  = re.findall(r'(.+)-ffnet_(\d+)\.txt', filename)
    assert len(tup)==1
    title, story_id = tup[0]
    title = title.lower()
    title = title.replace('_',' ')
    title = title.replace('.',' ')
    title = '_'.join([c.strip() for c in title.split()])
    if meta:
        return 'ffnet.meta.' + story_id + '.' + title + '.json'
    return 'ffnet.' + story_id + '.' + title + '.txt'

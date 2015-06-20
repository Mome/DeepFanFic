import os
import re
import sys
import xml

if sys.version_info < (3,0):
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser

categories = ['Category','Genre','Language','Characters','Status','Published','Updated','Packaged','Rating','Chapters','Words','Publisher','Story URL','Author URL','Summary']

filename = 'Your Basic Love Triangle_ Complete With Awkward...-ffnet_32716.txt'

def change_filename(filename):
    assert filename.endswith('.txt')
    uindex = len(filename) - filename.rindex('_')
    tup  = re.findall(r'(.+)-ffnet_(\d+)\.txt', filename)
    assert len(tup)==1
    title, story_id = tup[0]
    title = title.lower()
    title = title.replace('_',' ')
    title = title.replace('-',' ')
    title = title.replace('.',' ')
    title = title.replace('!',' ')
    title = title.replace('?',' ')
    title = '_'.join([c.strip() for c in title.split()])
    return 'ffnet-' + story_id + '-' + title + '.txt'

for filename in os.listdir('.'):
    with open(filename) as f:
        text = f.read()

    text = text.replace('\r\n', '\n')
    assert '\r' not in text

    print len(text),
    
    text = text[text.find('\n'*5):] # cut off meta information
    text = text[:-10] # cut off 'End file.'
    text = text.strip()

    print len(text),
    
    # remove html tags
    #remove_strings = ['<p>','<em>','<br>','<font>','<p>','<strong>','<meta name="Generator">','<div class="center">',
    #    '<div>','<meta name="ProgId">','<span>','<fido>','<meta name="Author">','<meta name="ProgId">','<hr>','< right>','<font "#000000"="">',
    #    '<meta name="GENERATOR">','<pont>']
    #for rs in remove_strings:
    #    text = text.replace(rs,'')

def remove_tags(text):
    return ''.join(xml.etree.ElementTree.fromstring(text).itertext())

    print len(text),

    # remove line breaks
    text = text.replace('\n\n','\r')
    text = text.replace('\n','')
    text = text.replace('\r','\n')

    print len(text),

    # remove wierd line starters

    lines = text.split('\n')
    for i,line in enumerate(lines):
        line = line.strip()
        if line.startswith(('_','>')):
            line = line[1:]
        if line.endswith(('_')):
            line = line[:-1]
        lines[i]=line
    text = '\n'.join(lines)

    print len(text),

    def remove_tags(text):
        return ''.join(xml.etree.ElementTree.fromstring(text).itertext())
 
    # ToDo: words having underscore stuff
    
    new_name = change_filename(filename)

    with open('../revised_stories/'+new_name,'w') as f:
        f.write(text)
    
    print filename, len(text),
    print re.findall(r'<.*>', text)
    raw_input()



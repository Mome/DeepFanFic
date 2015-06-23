import logging
import string
from textwrap import wrap
import xml

from base_writer import *

from fanficfare.html2text import html2text

class KludgeStringIO():
    def __init__(self, buf = ''):
        self.buflist=[]
    def write(self,s):
        try:
            s=s.decode('utf-8')
        except:
            pass
        self.buflist.append(s)
    def getvalue(self):
        return u''.join(self.buflist)
    def close(self):
        pass

class TextWriter(BaseStoryWriter):

    @staticmethod
    def getFormatName():
        return 'txt'

    @staticmethod
    def getFormatExt():
        return '.txt'

    def __init__(self, config, story):
        
        BaseStoryWriter.__init__(self, config, story)
        
        self.TEXT_FILE_START = string.Template(u'''
${title}
by ${author}
''')

        self.TEXT_TITLE_PAGE_START = string.Template(u'''
''')

        self.TEXT_TITLE_ENTRY = string.Template(u'''${label}: ${value}
''')

        self.TEXT_TITLE_PAGE_END = string.Template(u'''


''')

        self.TEXT_TOC_PAGE_START = string.Template(u'''

TABLE OF CONTENTS

''')

        self.TEXT_TOC_ENTRY = string.Template(u'''
${chapter}
''')
                          
        self.TEXT_TOC_PAGE_END = string.Template(u'''
''')

        self.TEXT_CHAPTER_START = string.Template(u'''

\t${chapter}

''')
        self.TEXT_CHAPTER_END = string.Template(u'')

        self.TEXT_FILE_END = string.Template(u'''

End file.
''')

    def writeStoryImpl(self, out):

        self.wrap_width = self.getConfig('wrap_width')
        if self.wrap_width == '' or self.wrap_width == '0':
            self.wrap_width = None
        else:
            self.wrap_width = int(self.wrap_width)
        
        wrapout = KludgeStringIO()
        
        if self.hasConfig("file_start"):
            FILE_START = string.Template(self.getConfig("file_start"))
        else:
            FILE_START = self.TEXT_FILE_START
            
        if self.hasConfig("file_end"):
            FILE_END = string.Template(self.getConfig("file_end"))
        else:
            FILE_END = self.TEXT_FILE_END
            
        # wrapout.write(FILE_START.substitute(self.story.getAllMetadata()))

        self.writeTitlePage(wrapout,
                            self.TEXT_TITLE_PAGE_START,
                            self.TEXT_TITLE_ENTRY,
                            self.TEXT_TITLE_PAGE_END)
        towrap = wrapout.getvalue()
        
        self.writeTOCPage(wrapout,
                          self.TEXT_TOC_PAGE_START,
                          self.TEXT_TOC_ENTRY,
                          self.TEXT_TOC_PAGE_END)

        towrap = wrapout.getvalue()
        wrapout.close()
        towrap = removeAllEntities(towrap)
        
        self._write(out,self.lineends(self.wraplines(towrap)))

        if self.hasConfig('chapter_start'):
            CHAPTER_START = string.Template(self.getConfig("chapter_start"))
        else:
            CHAPTER_START = self.TEXT_CHAPTER_START
        
        if self.hasConfig('chapter_end'):
            CHAPTER_END = string.Template(self.getConfig("chapter_end"))
        else:
            CHAPTER_END = self.TEXT_CHAPTER_END
        
        for index, (url, title,html) in enumerate(self.story.getChapters()):
            if html:
                logging.debug('Writing chapter text for: %s' % title)
                vals={'url':url, 'chapter':title, 'index':"%04d"%(index+1), 'number':index+1}
                self._write(out,self.lineends(self.wraplines(removeAllEntities(CHAPTER_START.substitute(vals)))))

                text = self.lineends(html2text(html,wrap_width=self.wrap_width))
                # remove html tags
                remove_strings = ['<p>','<em>','<br>','<font>','<p>','<strong>','<meta name="Generator">','<div class="center">',
                    '<div>','<meta name="ProgId">','<span>','<fido>','<meta name="Author">','<meta name="ProgId">','<hr>','< right>','<font "#000000"="">',
                    '<meta name="GENERATOR">','<pont>']
                for rs in remove_strings:
                    text = text.replace(rs,'')
                self._write(out, text)

                self._write(out,self.lineends(self.wraplines(removeAllEntities(CHAPTER_END.substitute(vals)))))

        #self._write(out,self.lineends(self.wraplines(FILE_END.substitute(self.story.getAllMetadata()))))
        #print(self.lineends(self.wraplines(FILE_END.substitute(self.story.getAllMetadata()))))
        #print html2text(html)

    def wraplines(self, text):
        
        if not self.wrap_width:
            return text
        
        result=''
        for para in text.split("\n"):
            first=True
            for line in wrap(para, self.wrap_width):
                if first:
                    first=False
                else:
                    result += u"\n"
                result += line
            result += u"\n"
        return result 

    ## The appengine will return unix line endings.
    def lineends(self, txt):
        txt = txt.replace('\r','')
        #if self.getConfig("windows_eol"):
        #    txt = txt.replace('\n',u'\r\n')
        return txt

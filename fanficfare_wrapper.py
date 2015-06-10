import subprocess

from utils import which

if not which('fanficfare'):
    raise UserWarning(
        """No fanficfare found, use:
           pip install fanficfare"""
    )


def list_story_urls(url, normalized=True):
    arg = '-n' if normalized else '-l'
    out = call_fff(url, arg)
    return out.split('\n')


def download_metadata(url):
    return call_fff(url, '-m')


def download_story(url):
    return call_fff(url)


def get_url_examples():
    return call_fff('',arg='-s').split('\n')


def call_fff(url, arg=None):
    args = ['fanficfare','--format=txt', url]
    if arg: args.insert(1,arg)
    out = subprocess.check_output(
        args=args,
        universal_newlines=True,
    )
    return out

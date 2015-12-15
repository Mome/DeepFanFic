import os
import readline
import sys


def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


def print_percent(num):
    num = int(num*100)
    if num < 10 :
        num = '0' + str(num)
    else :
        num = str(num)
    print('\b\b\b' + num + '%', end='')
    sys.stdout.flush()


def eprint(string):
    """erase and print"""
    if sys.version_info >= (3,3):
        w = os.get_terminal_size()[0]
        print(' '*w, end='\r')
    print(string, end='\r')
    sys.stdout.flush()


def rlinput(prompt, prefill=''):
    """Std-input with default value."""
    if prefill is None:
        prefill = ''
    if not isinstance(prefill, str):
        prefill = str(prefill)
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def rand_perm(x, prime):
    assert prime%4 == 3
    if x >= prime: return x
    residue = (x**2)%prime
    return residue if x<=prime/2 else prime-residue


def is_int(a):
    try:
        int(a)
    except:
        return False
    return True
    


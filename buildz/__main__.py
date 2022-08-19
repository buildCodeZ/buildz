#coding=utf-8
from buildz.build import test
from buildz import keys
import sys
def _main():
    v = sys.argv[1]
    lang = 'ch'
    if v in ['?', '-h', '--help']:
        if len(sys.argv)>2:
            lang = sys.argv[2].strip().lower()
        keys.help(lang)
    else:
        test()

pass
if __name__=="__main__":
    _main()

pass

#
import os
import sys

from buildz.fz import dirz as dirs
from buildz.fz import fio
dirs.Deal = dirs.FileDeal
#from filez import dirs
import re
class Deal(dirs.Deal):
    def init(self):
        super().init()
        self.ignore_files = [
            '.*\.py[cod]$',
            '.*py\.class$',
            '.*\.dt',
            '.*\.log'
        ]
        self.ignore_dirs=[
            '__pycache__',
            'chromeCache',
            '.*\.git',
            '.*\.egg-info',
            '.*/dist'
        ]
    def check_ignore(self, filepath, isdir):
        if not isdir:
            for pt in self.ignore_files:
                if len(re.findall(pt, filepath))>0:
                    return True
        else:
            for pt in self.ignore_dirs:
                if len(re.findall(pt, filepath))>0:
                    return True
        return False
    def visit(self, fileinfo, depth):
        isdir = fileinfo.isdir
        filepath = fileinfo.path
        if self.check_ignore(filepath, isdir):
            print(f"ignore path: {filepath}, isdir: {isdir}")
            return False
        if not isdir:
            bs = fio.read(filepath)
            bs =bs.replace(b"\r\n", b"\n")
            fio.write(bs, filepath)
        return True
    def catch(self, fileinfo, depth, exp):
        isdir = fileinfo.isdir
        filepath = fileinfo.path
        print(f"exp in {filepath} isdir={isdir}: {exp}")
        pass

pass


def test():
    dp = sys.argv[1]
    Deal().dirs(dp)

pass

if __name__=="__main__":
    test()

pass

#
import os
import sys

from buildz.fz import dirz as dirs
dirs.Deal = dirs.FileDeal
#from filez import dirs
import re
class Removes(dirs.Deal):
    def init(self):
        super(self.__class__, self).init()
        self.dps = []
    def result(self):
        self.dps.sort(key = lambda x:len(x),reverse=True)
        print("dps:", self.dps)
        for dp in self.dps:
            os.rmdir(dp)
        return self.dps
    def visit(self, fileinfo, depth):
        isdir = fileinfo.isdir
        filepath = fileinfo.path
        if not isdir:
            os.remove(filepath)
            return False
        self.dps.append(filepath)
        return True

pass
class Deal(dirs.Deal):
    def visit(self, fileinfo, depth):
        isdir = fileinfo.isdir
        filepath = fileinfo.path
        if not isdir:
            return False
        dp = filepath
        dirname = os.path.basename(dp)
        #if dirname[:1] == ".":
        #    return False
        if dirname not in ("__pycache__", "chromeCache"):
            return True
        Removes().dirs(dp)
        #os.removedirs(dp)
        return False
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

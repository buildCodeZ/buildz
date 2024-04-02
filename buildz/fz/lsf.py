#coding=utf-8

from . import dirz

import re
class ListsDeal(dirz.FileDeal):
    def result(self):
        return self.fps, self.errors
    def init(self):
        super().init()
        self.fps = []
        self.errors = []
    def visit(self, fp, isdir, depth):
        self.fps.append([fp, isdir])
        return True
    def catch(self, fp, isdir, depth, exp):
        self.errors.append([fp, isdir, exp])

pass

class FileSearchDeal(dirz.FileDeal):
    def init(self, pt_fp=None, pt = None, depth = None):
        super().init()
        self.pt_fp = pt_fp
        if type(pt) == str:
            pt = pt.encode()
        self.pt = pt
        self.rst = []
        self.depth = depth
    def result(self):
        return self.rst
    def visit(self, filepath, isdir, depth):
        if self.depth is not None and depth > self.depth:
            return False
        if isdir:
            return True
        if self.pt_fp is not None and len(re.findall(self.pt_fp, filepath))==0:
            return False
        if self.pt is not None:
            try:
                with open(filepath, 'rb') as f:
                    s = f.read()
            except Exception as exp:
                print("fread exp in :", filepath, "exp:", exp)
                return False
            if len(re.findall(self.pt, s))==0:
                return False
        #print("find:", filepath)
        self.rst.append(filepath)
        return False
    def catch(self, filepath, isdir, depth, exp):
        print(f"exp in {filepath} isdir={isdir}: {exp}")
        pass

pass


def lists(fp):
    return ListsDeal().dirs(fp)

pass
def search(dp, pt_fp = None, pt = None, depth = None):
    return FileSearchDeal(pt_fp, pt, depth).dirs(dp)

pass

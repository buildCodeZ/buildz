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
    def visit(self, finfo, depth):
        fp, isdir = finfo.path, finfo.isdir
        self.fps.append([fp, isdir])
        return True
    def catch(self, finfo, depth, exp):
        fp, isdir = finfo.path, finfo.isdir
        self.errors.append([fp, isdir, exp])

pass

class SearchDeal(dirz.FileDeal):
    def init(self, pt_fp=None, pt = None, pt_dp = None, depth = None, relative = False):
        super().init()
        self.pt_fp = pt_fp
        self.pt_dp = pt_dp
        if type(pt) == str:
            pt = pt.encode()
        self.pt = pt
        self.rst = []
        self.errs = []
        self.depth = depth
        self.relative = relative
    def fps(self, keep_dir = False, relative = None, fp_only = True):
        if relative is None:
            relative = self.relative
        rst = self.rst
        if relative:
            rst = [[i.rpath, i.isdir] for i in rst]
        else:
            rst = [[i.path, i.isdir] for i in rst]
        if not keep_dir:
            rst = [k for k in rst if not k[1]]
        if fp_only:
            rst = [k[0] for k in rst]
        return rst
    def result(self):
        return self.rst
    def visit(self, finfo, depth):
        if self.depth is not None and depth > self.depth:
            return False
        filepath = finfo.path
        isdir = finfo.isdir
        if self.relative:
            filepath = finfo.rpath
        if isdir:
            if finfo.empty_dir or depth==self.depth:
                if self.pt_dp is not None and len(re.findall(self.pt_dp, filepath))==0:
                    return True
                self.rst.append(finfo)
            return True
        if self.pt_fp is not None and len(re.findall(self.pt_fp, filepath))==0:
            return False
        if self.pt is not None:
            try:
                with open(filepath, 'rb') as f:
                    s = f.read()
            except Exception as exp:
                self.catch(finfo, depth, exp)
                return False
            if len(re.findall(self.pt, s))==0:
                return False
        self.rst.append(finfo)
        return False
    def catch(self, finfo, depth, exp):
        filepath = finfo.path
        if self.relative:
            filepath = finfo.rpath
        print(f"exp in {finfo}: {exp}")
        self.errs.append([finfo, exp])
        pass

pass

def lists(fp):
    return ListsDeal().dirs(fp)

pass
def _search(dp, pt_fp = None, pt = None, pt_dp = None, depth=None, relative = False):
    deal = SearchDeal(pt_fp, pt, pt_dp, depth,relative)
    return deal.dirs(dp)

pass
def searchs(dp, pt_fp = None, pt = None, pt_dp = None, depth=None, relative = False):
    deal = SearchDeal(pt_fp, pt, pt_dp, depth,relative)
    deal.dirs(dp)
    return deal.fps(keep_dir=True, fp_only=False)

pass
def searchd(dp, pt_fp = None, pt = None, pt_dp = None, depth=None, relative = False):
    deal = SearchDeal(pt_fp, pt, pt_dp, depth,relative)
    deal.dirs(dp)
    return deal.fps(keep_dir=True, fp_only=True)

pass

def search(dp, pt_fp = None, pt = None, depth=None, relative = False):
    deal = SearchDeal(pt_fp, pt, None, depth,relative)
    deal.dirs(dp)
    return deal.fps(keep_dir=False, fp_only=True)

pass
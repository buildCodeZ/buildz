
import sys
import os
def load(md, fc = None):
    """
        import object(whether module or others) from md(or md.fc)
        exp:
            load("buildz.xf") = package xf
            load("buildz.xf", "loads") = function loads from package buildz.xf
            load("buildz.xf.loads") = function loads from package buildz.xf
    """
    mds = md.split(".")
    arr = mds[1:]
    while len(mds)>0:
        try:
            md = __import__(".".join(mds))
            break
        except:
            mds = mds[:-1]
    if len(mds)==0:
        raise Exception("can't import package from "+md)
    for k in arr:
        md = getattr(md, k)
    if fc is not None:
        fc = getattr(md, fc)
    else:
        fc = md
    return fc

pass
def pyexe():
    return sys.executable

pass
exe=pyexe
is_windows = sys.platform.lower()=='win32'
def pypkg():
    """
        return python package path, test on linux and windows
    """
    import site
    sites = site.getsitepackages()
    if is_windows:
        fpath = sites[-1]
    else:
        fpath = sites[0]
    return fpath

pass
pkg = pypkg
pth = pypkg

class Pth:
    def __init__(self, fp = "build.pth"):
        self.fp = os.path.join(pth(), fp)
    def read(self):
        fp = self.fp
        if not os.path.isfile(fp):
            return []
        with open(fp, 'rb') as f:
            s = f.read().decode()
        return s.split("\n")
    def add(self, path):
        arr = self.read()
        if path in arr:
            print("alread add")
            return
        arr.append(path)
        self.write(arr)
    def write(self, paths = []):
        if type(paths) not in [list, tuple]:
            paths = [paths]
        s = "\n".join(paths)
        with open(self.fp, 'wb') as f:
            f.write(s.encode())
    def remove(self):
        os.remove(self.fp)

pass

_pth = Pth()

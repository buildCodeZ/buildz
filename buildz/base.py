#coding=utf-8
import builtins
import os
str = builtins.str
int = builtins.int
float = builtins.float
str = builtins.str
class Map:
    Key = object()
    def __dir__(self):
        return dir(Map)
    def __init__(self, obj = None, **maps):
        if obj is None:
            obj = {}
        else:
            obj = dict(obj)
        obj.update(maps)
        self.__dict__[Map.Key] = obj
    def __call__(self, **maps):
        if len(maps)==0:
            return self.__dict__[Map.Key]
        self().update(maps)
        return self
    def __getattr__(self, key):
        if key not in self():
            return None
        return self()[key]
    def __getitem__(self, key):
        if key not in self():
            return None
        return self()[key]
    def __setitem__(self, key, val):
        maps = self()
        maps[key] = val
    def __setattr__(self, key, val):
        maps = self()
        maps[key] = val

pass

def list(*argv):
    return builtins.list(argv)

pass

def dict(**maps):
    return builtins.dict(maps)

pass
def val(v):
    return v

pass

def add(*argv):
    rst = argv[0]
    for v in argv[1:]:
        rst += v
    return rst

pass

def join(*argv):
    return os.path.join(*argv)

pass


class SimpleDeal:
    def deal(self, filepath, isdir, depth):
        return True

pass

def listdir(path, deal = None, depth = 0):
    files = os.listdir(path)
    files = [os.path.join(path, file) for file in files]
    rst = []
    for file in files:
        if os.path.isdir(file):
            if deal(file, True, depth+1):
                listdir(file, deal, depth+1)
        else:
            deal(file, False, depth+1)
    return rst

pass


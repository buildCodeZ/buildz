#coding=utf-8
import builtins
import os
str = builtins.str
int = builtins.int
float = builtins.float
str = builtins.str
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


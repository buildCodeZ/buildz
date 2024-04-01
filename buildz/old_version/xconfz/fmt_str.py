#coding=utf-8


"""
impl in class
"""

import io
# io.StringIO("asdf")
from .buff import *
from .fc import *

from .fmt_base import *
from .fmt_type import *
from .mg import *



class StrForamt(BaseFormat):
    def __init__(self, reg, symbol = '"', bts = False, single = True, t_single = False):
        self.symbol = symbol
        self.reg = reg
        self.bts = bts
        self.single = single
        self.t_single = t_single
    def c(self, ch):
        if self.bts and type(ch)==str:
            ch = ch.encode("utf-8")
        return ch
    def f(self, fc, *args, **maps):
        args = [self.c(k) for k in args]
        maps = {k:self.c(maps[k]) for k in maps}
        return fc(*args, **maps)
    def deal(self, node, fc, **params):
        if not node.is_leaf():
            return None
        val = node.value
        if type(val) not in [str, bytes]:
            return None
        if self.single and self.f(val.find, "\n")>=0:
            return None
        if not self.reg.exist(val) and val.strip()!="":
            return val
        val = self.f(val.replace, "\\", "\\\\")
        if self.t_single:
            val = self.f(val.replace, "\n", "\\n")
        val = self.f(val.replace, "\"", "\\\"")
        return self.symbol+val+self.symbol

pass

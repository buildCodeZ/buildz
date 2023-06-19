#coding=utf-8


"""
impl in class
"""

import io
# io.StringIO("asdf")
from buildz.xconfz.buff import *
from buildz.xconfz.fc import *


class Confz:
    def fcs(self, fc, *args, **maps):
        return fc(*self.cs(*args), **maps)
    def add_fc(self, fc, *args, **maps):
        obj = self.fcs(fc, *args, **maps)
        self.add(obj)
        return self
    def add_top_fc(self, fc, *args, **maps):
        obj = self.fcs(fc, *args, **maps)
        self.add_top(obj)
        return self
    def cs(self, *args):
        return [self.c(k) for k in args]
    def c(self, s):
        if self.bts:
            s = s.encode("ascii")
        return s
    def add(self,obj):
        obj.init(self.reg)
        self.prevs.append(obj.prev)
        self.deals.append(obj.deal)
        return self
    def add_top(self, obj):
        obj.init(self.reg)
        self.prevs=[obj.prev]+self.prevs
        self.deals=[obj.deal]+self.deals
        return self
    def do(self, fcs, buff, stack):
        for fc in fcs:
            if fc(buff, stack):
                #print("fc:", fc)
                return True
        return False
    def __init__(self, bts= False):
        self.bts= bts
        self.deals = []
        self.prevs = []
        self.reg = Reg()
    def load(self, reader):
        buff = BufferImpl(reader, "" if not self.bts else b"")
        queue = []
        while self.do(self.prevs, buff, queue):
            pass
        #print("queue:", [it.val for it in queue])
        stack = []
        while self.do(self.deals, queue, stack):
            #print("QUEUE:", queue)
            #print("STACK:", stack)
            #print("*"*30)
            pass
        if len(stack)==0:
            raise Exception("ERROR not data")
        if len(stack)==1:
            return stack[0].val
        else:
            return [it.val for it in stack]

pass
class Map:
    def __init__(self):
        self.maps = {}
    def set(self, key, val):
        self.maps[key] = val
    def __call__(self, s):
        if s not in self.maps:
            raise Exception("Error key:"+s)
        return self.maps[s]

pass
def get_none(s):
    return None

pass


def build(bts = False):
    cfz = Confz(bts)
    cfz.add_fc(SpcDeal)

    cfz.add_fc(SetDeal, ":").add_fc(SetDeal,"=")
    types = TypesDeal()
    types.add_deal(cfz.fcs(TypeDealB, "|"))
    types.add_deal(cfz.fcs(TypeDealA, "<", ">"))

    types.add_type("int", int)
    types.add_type("i", int)
    types.add_type("float", float)
    types.add_type("f", float)
    types.add_type("str", str)
    types.add_type("s", str)

    get_bool = Map()
    get_bool.set("true", True)
    get_bool.set("1", True)
    get_bool.set("false", False)
    get_bool.set("0", False)

    types.add_type("bool", get_bool)
    types.add_type("b", get_bool)
    types.add_type("null", get_none)
    types.add_type("nil", get_none)
    types.add_type("~", get_none)

    cfz.add(types)


    cfz.add_fc(StrDeal,*["###"]*2, note = True)
    cfz.add_fc(StrDeal,"#", "\n", single_line = True, note = True)
    cfz.add_fc(StrDeal,"//", "\n", single_line = True, note = True)
    #cfz.add_fc(StrDeal,*["'''"]*2)
    #cfz.add_fc(StrDeal,*['"""']*2)
    #cfz.add_fc(StrDeal,*["'"]*2, single_line = True)
    #cfz.add_fc(StrDeal,*['"']*2, single_line = True)


    cfz.add_fc(StrDeal,"r'''", "'''")
    cfz.add_fc(StrDeal,'r"""', '"""')

    cfz.add_fc(StrDeal,"r'", "'", single_line = True)
    cfz.add_fc(StrDeal,'r"', '"', single_line = True)

    cfz.add_fc(TranslateStrDeal,"'''", "'''")
    cfz.add_fc(TranslateStrDeal,'"""', '"""')

    cfz.add_fc(TranslateStrDeal,"'", "'", single_line = True)
    cfz.add_fc(TranslateStrDeal,'"', '"', single_line = True)
    
    cfz.add_fc(ItemDeal, ",").add_fc(ItemDeal, "\n").add_fc(ItemDeal, ";")
    cfz.add_fc(ListDeal, "[", "]")
    cfz.add_fc(ListDeal, "(", ")")
    cfz.add_fc(MapDeal, "{", "}")
    cfz.add_fc(NextCharDeal)
    return cfz

pass
import io
def loads(s):
    cfz = build(type(s)==bytes)
    return cfz.load(io.StringIO(s).read)

pass

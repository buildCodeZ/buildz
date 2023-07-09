#coding=utf-8


"""
impl in class
"""

import io
# io.StringIO("asdf")
from buildz.xconfz.buff import *
from buildz.xconfz.fc import *

from buildz.xconfz.fmt_base import *
from buildz.xconfz.fmt_type import *
from buildz.xconfz.fmt_str import *
from buildz.xconfz.mg import *

class Buildz:
    def __init__(self, bts= False):
        self.bts= bts
        self.deals = {}
        self._default = None
    def default(self, _def):
        self._default = _def
    def fcs(self, fc, *args, **maps):
        return fc(*self.cs(*args), **maps)
    def set_fc(self, type, fc, *args, **maps):
        obj = self.fcs(fc, *args, **maps)
        self.set(type, obj)
        return self
    def cs(self, *args):
        return [self.c(k) for k in args]
    def c(self, s):
        if self.bts:
            s = s.encode("utf-8")
        return s
    def set(self, type, fc):
        self.deals[type] = fc
    def __call__(self, data):
        tp = type(data)
        if tp not in self.deals:
            return self._default(data, self)
        return self.deals[tp](data, self)

pass

class Outputz(Confz):
    def __init__(self, bts= False):
        self.bts= bts
        self.deals = []
    def add(self,obj):
        self.deals.append(obj)
        return self
    def add_top(self, obj):
        self.deals=[obj]+self.deals
        return self
    def __call__(self, data, **params):
        for deal in self.deals:
            val = deal(data, self, **params)
            if val is not None:
                return val
        return None

pass
class Formatz:
    def __init__(self, bts = False):
        self.build = Buildz(bts)
        self.output = Outputz(bts)
    def __call__(self, data, **params):
        node = self.build(data)
        rst = self.output(node, **params)
        return rst

pass
class JsonFormat(BaseFormat):
    def deal(self, node, fc, **params):
        import json
        if not node.is_leaf():
            return None
        value = node.value
        if value is None:
            return None
        return json.dumps(node.value)

pass
def build_format(bts = False, size = 4, format = False, simple = 1, simple_size = 1, loads = None, as_json =False, t_single = True):
    if loads is None:
        loads = build()
    fmtz = Formatz(bts)
    fmtz.build.default(ItemFormat())
    fmtz.build.set_fc(list, ListFormat,"[", "]")
    fmtz.build.set_fc(tuple, ListFormat,"(", ")")
    fmtz.build.set_fc(dict, MapFormat,"{","}")


    types = TypesDealFormat()
    #types.add_deal(fmtz.output.fcs(TypeDealBFormat, "|"))
    types.add_deal(fmtz.output.fcs(TypeDealAFormat, "<", ">", ","))

    types.add_type(int, lambda x:[str(x), "i"])
    types.add_type(float, lambda x:[str(x), "f"])
    types.add_type(str, lambda x:[str(x), "s"])
    types.add_type(bool, lambda x:[str(x), "b"])
    types.add_type(type(None), lambda x:[str(x), "nil"])
    types.init()

    fmtz.output.add_fc(NodeFormat)
    fmtz.output.add_fc(SymbolFormat)
    spt = ","
    if not format:
        simple_size = 0
        spt = ", "
    fmtz.output.add_fc(KeyFormat, spt, SptFormatNode)
    fmtz.output.add_fc(KeyFormat, ": ", KVFormatNode)
    fmtz.output.add_fc(SpcFormat, " ", "\n", size = size, format = format, simple = simple, simple_size = simple_size)
    if as_json:
        fmtz.output.add_fc(JsonFormat)
    fmtz.output.add_fc(StrForamt, loads.reg, '"', bts, not t_single, t_single)
    fmtz.output.add_fc(StrForamt, loads.reg, '"""', bts, False)
    fmtz.output.add(types)
    return fmtz

pass
def dumps(data, bts = False, size = 4, format = False, simple = 1, simple_size = 1, as_json =False, t_single = True):
    fmtz = build_format(bts=bts, size = size, format = format, simple = simple, simple_size = simple_size, as_json =as_json, t_single =t_single)
    nd = fmtz(data)
    return nd

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

#

from ..tools import *
from buildz.ioc import wrap
@wrap.obj(id="verify")
@wrap.obj_args("ref, log", "ref, cache_modify")
class Verify(Base):
    def init(self, log, upd):
        self.log = log
        self.upd = upd
    def match(self, v, val, result, data):
        tp,v = v
        if tp=="=":
            if type(val)!=type(v):
                if type(v)==str:
                    val = str(val)
                elif type(val)==str:
                    v = str(v)
            return val==v
        elif tp == ">":
            if val is None:
                return False
            if type(val)==str:
                val = float(val)
            return val>v
        elif tp=="<":
            if val is None:
                return False
            if type(val)==str:
                val = float(val)
            return val<v
        elif tp==">=":
            if val is None:
                return False
            if type(val)==str:
                val = float(val)
            return val>=v
        elif tp=="<=":
            if val is None:
                return False
            if type(val)==str:
                val = float(val)
            return val<=v
        elif tp=="sh":
            return eval(v)
        else:
            err = f"not impl match type: {tp}"
            self.log.error(err)
            raise Exception(err)
    def call(self, data, fc=None):
        result = self.upd(xf.g(data, result = {}))
        vs = self.upd(xf.g(data, verify=[]))
        for k,v in vs:
            bak = v
            if k == "$":
                if type(v)!=list:
                    v = ["sh", v]
                val = None
            else:
                val = xf.gets(result, k.split("."))
            if type(v)!=list:
                v = ["=", v]
            jg = self.match(v, val, result, data)
            if not jg:
                self.log.error(f"verify failed in {data}, key: '{k}', match: {bak}, val: {val}")
                return False
        if fc is None:
            return True
        return fc(data)

pass
            
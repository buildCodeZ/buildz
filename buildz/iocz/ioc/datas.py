
from buildz import pyz, dz
from .tdata import TData
class Datas(TData):
    def init(self, id=None, ns=None, dts=None):
        super().init(id,ns)
        self.dts = dts
    def bind(self, dts):
        self.dts = dts
    def set(self, key, val, tag=None):
        tag = pyz.nnull(tag, self.default)
        super().set(key, val, tag)
        if self.dts is not None:
            if tag == Key.pub:
                self.dts.set(key, val, self.ns)
            elif tag == Key.ns:
                self.dts.ns_set(key, val, self.ns)
    def tget(self, key, src=None,id=None, gfind=True):
        ns, id = self.nsid(src, id)
        obj, find=super().tget(key, src, id)
        if not find and gfind:
            obj, find = self.dts.get(key, ns, id)
        return obj, find

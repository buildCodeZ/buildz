#
from .tdata import TData
class Deals(TData):
    def init(self, mg=None, id=None, ns=None):
        self.mg = mg
        super().init(id,ns)
    def bind(self, mg):
        self.mg = mg
    def tget(self, key, src=None,id=None):
        ns, id = self.nsid(src, id)
        obj,find=super().tget(key, src, id)
        if not find:
            obj,find = self.mg.get_deal(key, src, id)
        return obj, find
#
from .tdata import TData, TNData
class Unit(Base):
    def init(self, id=None, ns=None, deals=None):
        self.id = id
        self.ns = ns
        self.confs = Datas(id, ns)
        self.encapes = Datas(id, ns)
        self.deals = deals
        self.mg = None
    def bind(self, mg):
        self.mg = mg
        self.confs.bind(mg.confs)
        self.deals.bind(mg.deals)
    def get_deal(self, key, src=None, id=None, gfind=True):
        return self.deals.tget(key, src, id, gfind)
    def get_conf(self, key, src=None, id=None, gfind=True):
        return self.confs.tget(key, src, id, gfind)
    def get_encape(self, key, src=None, id=None, gfind=True):
        obj, find = self.encapes.tget(key, src, id)
        if not find:
            conf, cfind = self.get_conf(key, src, id, False)
            if not cfind:
                return None, 0
            
            deal, dfind = self.get_deal(key, src, id)
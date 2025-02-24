from ..ioc.base import *
from ..ioc.confs import Confs
class BaseEncape(Encape):
    @staticmethod
    def obj(val,*a,**b):
        if not isinstance(val, Encape):
            return val
        return val(*a,**b)

pass
class BaseDeal(Deal):
    def init(self):
        self.cache_encapes = {}
    def cache_get(self, key, ns):
        if key is None:
            return None
        key = (ns, key)
        return dz.get(self.cache_encapes, key, None)
    def cache_set(self, key, ns, encape):
        if key is None:
            return
        key = (ns, key)
        self.cache_encapes[key] = encape
    @staticmethod
    def get_encape(key, unit):
        if Confs.is_conf(key):
            ep,_,find = unit.get_encape(key, unit)
            assert find
            return ep
        return key

pass

class Params(Base):
    def clone(self, **upds):
        args, maps = list(self.args), dict(self.maps)
        maps.update(upds)
        return Params(args, maps)
    def init(self, *args, **maps):
        self.args = args
        self.maps = maps
    def get(self, key, default=None):
        if key not in self.maps:
            return default
        return self.maps[key]
    def __getattr__(self, key):
        if key not in self.maps:
            return None
        return self.maps[key]

pass
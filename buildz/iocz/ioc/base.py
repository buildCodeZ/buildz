from ..base import *
basepath = path
path = pathz.Path()
path.set("conf", basepath.local("ioc/conf"), curr=0)
class Encape(Base):
    def call(self, params=None, **maps):
        return None

pass
class Deal(Base):
    def deal(self, conf, unit):
        return None
    def call(self, conf, unit):
        'encape, conf, conf_need_udpate'
        encape = self.deal(conf,unit)
        return encape,conf,False

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
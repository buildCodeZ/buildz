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

from ..ioc.base import *
from ..ioc.confs import Confs
from ... import dz
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
    def call(self, conf, unit):
        'encape, conf, conf_need_udpate'
        id,find=unit.conf_key(conf)
        ns = unit.ns
        encape = self.cache_get(id, ns)
        if encape is not None:
            return encape, conf, False
        conf, upd = self.update(conf, unit)
        encape = self.deal(conf,unit)
        self.cache_set(id, ns, encape)
        return encape,conf,upd

pass

#

from .base import *
from .encapes import Encapeset
from .dataset import Dataset
from ... import pyz,dz
from .ids import Ids
from .unit import Unit
from .builds import Buildset
class StrDealKey(Base):
    def init(self, key):
        self.key = key
    def call(self, conf):
        if self.key not in conf:
            return None
        return conf[self.key]

pass
class Manager(Base):
    @staticmethod
    def make_deal_key(deal_key):
        if type(deal_key) == str:
            deal_key = StrDealKey(deal_key)
        return deal_key
    @staticmethod
    def make_ids(ids):
        if type(ids)==str:
            ids = Ids(ids)
        return ids
    def init(self, ids, deal_key, deal_ids = None):
        self._index = 0
        self.units = {}
        self.builds = Buildset(self)
        ids = self.make_ids(ids)
        self.ids = ids
        self.deal_key = self.make_deal_key(deal_key)
        self.deal_ids = pyz.nnull(deal_ids, ids)
        self.confs = Dataset(self.ids)
        self.deals = Dataset(self.deal_ids)
        self.encapes = Encapeset(self.ids, self)
        self.default_unit = self.create()
    def add_build(self, conf):
        self.builds.add(conf)
    def build(self):
        self.builds.build()
    def add(self, unit):
        unit.bind(self)
        self.units[unit.id] = unit
    def create(self, ns=None, deal_ns = None, deal_key=None):
        id = self.id()
        deal_key = pyz.nnull(deal_key, self.deal_key)
        deal_key = self.make_deal_key(deal_key)
        unit = Unit(ns, deal_ns, deal_key, id)
        unit.bind(self)
        return unit
    def get_unit(self, id):
        if id not in self.units:
            return self.default_unit
        return self.units[id]
    def id(self):
        index = self._index
        self._index+=1
        return index
    def get_deal(self, key, ns=None, id=None):
        return self.deals.tget(key, ns, id)
    def set_deal(self, key, deal, ns=None, tag=None, id=None):
        self.deals.set(key, deal, ns, tag, id)
    def get_conf(self, key, ns=None, id=None):
        return self.confs.tget(key, ns, id)
    def set_conf(self, key, conf, ns=None, tag=None, id=None):
        self.confs.set(key, conf, ns, tag, id)
    def get_encape(self, key, ns=None, id=None):
        self.build()
        return self.encapes.tget(key, ns, id)
    def set_encape(self, key, encape, ns=None, tag=None, id=None):
        self.encapes.set(key, encape, ns, tag, id)

pass

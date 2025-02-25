#
from .base import *
from .datas import Datas
from .confs import Confs
from .encapes import Encapes
from ... import pyz
from .builds import Builds
class Unit(Base):
    def init(self, ns=None, deal_ns=None, deal_key = None, conf_key = None, id=None):
        self.ns = ns
        self.deal_ns = deal_ns
        self.deal_key = deal_key
        self.conf_key = conf_key
        self.id = id
        self.confs = Confs(ns, deal_ns, id)
        self.deals = Datas(deal_ns, id)
        self.builds = Builds(self)
        self.mg = None
        self.build_encapes()
    def add_build(self, conf):
        self.builds.add(conf)
    def build(self):
        self.builds.build()
    def is_conf(self, obj):
        return self.confs.is_conf(obj)
    def build_encapes(self):
        if self.confs is None or self.deals is None or self.deal_key is None:
            self.encapes = None
            return
        self.encapes = Encapes(self.ns, self.id, None, self)
    def bind(self, mg):
        if self.mg == mg:
            return
        self.mg = mg
        self.deal_key = pyz.nnull(self.deal_key, mg.deal_key)
        self.conf_key = pyz.nnull(self.conf_key, mg.conf_key)
        if self.id is None:
            self.id = mg.id()
            self.confs.set_id(self.id)
            self.deals.set_id(self.id)
        self.mg.add(self)
        self.builds.bind(mg.builds)
        self.confs.bind(mg.confs)
        self.deals.bind(mg.deals)
        self.build_encapes()
        self.encapes.bind(mg.encapes)
    def get_deal(self, key, src=None, id=None, gfind=True):
        return self.deals.tget(key, src, id, gfind)
    def set_deal(self, key, deal, tag=None):
        self.deals.set(key, deal, tag)
    def get_conf(self, key, src=None, id=None, gfind=True):
        return self.confs.tget(key, src, id, gfind)
    def set_conf(self, key, conf, tag=None):
        self.conf_key.fill(conf, key)
        self.confs.set(key, conf, tag)
    def get_encape(self, key, src=None, id=None, gfind=True):
        self.build()
        return self.encapes.tget(key, src, id, gfind)
    def set_encape(self, key, encape, tag=None):
        self.encapes.set(key, encape, tag)
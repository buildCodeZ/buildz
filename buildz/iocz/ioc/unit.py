#
from .base import *
from .datas import Datas
from .tdata import TagData, UnitBase
from .confs import Confs
from .encapes import Encapes
from ... import pyz
from .builds import Builds
from .envs import Envs
class Unit(UnitBase):
    def nsid(self, src=None, id=None):
        if src == -1:
            src = self
        if isinstance(src, UnitBase) or isinstance(src, TagData):
            src,id = src.ns, src.id
        return src, id
    def init(self, ns=None, deal_ns=None, env_ns=None, deal_key = None, conf_key = None, id=None):
        super().init(ns, id)
        self.deal_ns = deal_ns
        self.env_ns = env_ns
        self.deal_key = deal_key
        self.conf_key = conf_key
        self.confs = Confs(ns, deal_ns, id)
        self.deals = Datas(deal_ns, id)
        self.envs = Envs(env_ns, id)
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
            self.envs.set_id(self.id)
        self.mg.add(self)
        self.builds.bind(mg.builds)
        self.confs.bind(mg.confs)
        self.deals.bind(mg.deals)
        self.envs.bind(mg.envs)
        self.build_encapes()
        self.encapes.bind(mg.encapes)
    def get_env(self, key, src=-1, id=None, gfind=True):
        src, id = self.nsid(src, id)
        return self.envs.tget(key, src, id, gfind)
    def set_env(self, key, val, tag=None):
        self.envs.set(key, val, tag)
    def get_deal(self, key, src=-1, id=None, gfind=True):
        src, id = self.nsid(src, id)
        return self.deals.tget(key, src, id, gfind)
    def set_deal(self, key, deal, tag=None):
        self.deals.set(key, deal, tag)
    def get_conf(self, key, src=-1, id=None, gfind=True):
        src, id = self.nsid(src, id)
        return self.confs.tget(key, src, id, gfind)
    def set_conf(self, key, conf, tag=None):
        self.conf_key.fill(conf, key)
        self.confs.set(key, conf, tag)
    def get_encape(self, key, src=-1, id=None, gfind=True):
        src, id = self.nsid(src, id)
        self.mg.build()
        return self.encapes.tget(key, src, id, gfind)
    def set_encape(self, key, encape, tag=None):
        self.encapes.set(key, encape, tag)
    def get_var(self, key, src=-1, tag=None):
        src, id = self.nsid(src, None)
        return self.mg.get_var(key, src, tag)
    def get(self, key, src=-1, id=None, gfind=True, params=None, search_var=True):
        src, id = self.nsid(src, id)
        if search_var:
            obj, find = self.mg.get_var(key, src, TagData.Key.Ns)
            if find:
                return obj, 1
        encape, _tag, find = self.get_encape(key, src, id, gfind)
        if not find:
            return None, 0
        return encape(params),1
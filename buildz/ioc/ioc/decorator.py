#coding=utf-8
from buildz.base import Base
from buildz import xf
from threading import Lock
class Decorator(Base):
    def init(self):
        #self.conf = {}
        self.confs = {}
        self.confs[None] = {}
        self.objs = {}
        self.ids = {}
        self.namespace = None
        self.fcs = {}
        self._ns = {}
        self.regist("add_datas", self.add_datas)
    def get_conf_obj(self, ns):
        return self.objs[ns]
    @property
    def conf(self):
        return self.get_conf_obj(self.namespace)
    def fcns(self, namespace, fc):
        self._ns[fc] = namespace
    def ns(self, namespace):
        self.namespace = namespace
    def curr_ns(self):
        return self.namespace
    def regist(self, key, fc):
        self.fcs[key] = fc
    def get_conf(self, src, ns = None):
        if ns is None:
            ns = self.namespace
        if src in self._ns:
            ns = self._ns[src]
        if ns not in self.confs:
            conf = {}
            conf['namespace'] = ns
            self.confs[ns] = conf
        return self.confs[ns]
    def get(self, tag, index, src=None):
        conf = self.get_conf(src)
        if tag not in conf:
            conf[tag]=[]
        return conf[tag][index]
    def add(self, tag, data, src = None, ns = None):
        conf = self.get_conf(src, ns)
        if tag not in conf:
            conf[tag]=[]
        id = len(conf[tag])
        conf[tag].append(data)
        return id
    def set(self, tag, key, val, src=None):
        conf = self.get_conf(src)
        if tag not in conf:
            conf[tag]={}
        conf[tag][key]=val
    def add_datas(self, item, key=None, ns = None):
        if type(item)==str:
            item = xf.loads(item)
        return self.add("datas", item, key, ns)
    def get_datas(self, id, key=None):
        return self.get("datas", id, key)
    def set_datas(self, id, val):
        return self.set("datas", id, val)
    def set_envs(self, key, val):
        return self.set("env", key, val)
    def add_inits(self, val):
        return self.add("inits", val)
    def add_locals(self, item):
        return self.add("locals", item)
    def bind_confs(self, confs):
        for ns, val in self.confs.items():
            id = confs.add(val)
            obj = confs.get_conf(id)
            self.ids[ns] = id
            self.objs[ns] = obj
    def all(self):
        arr = [val for k,val in self.confs.items()]
        return arr
    # def call(self):
    #     return self.conf

pass

decorator = Decorator()
class Fcs:
    def __init__(self, k, ns):
        self._ioc_ns = [k, ns]
    @property
    def conf(self):
        return self._ioc_ns[1].get_conf(self._ioc_ns[0])

pass
class NameSpace(Base):
    def get_conf(self, ns):
        return self.decorator.get_conf_obj(ns)
    def init(self, decorator):
        self.decorator = decorator
        self.lock = Lock()
    def fc(self, namespace, rfc):
        def wfc(*a, **b):
            with self.lock:
                ns = self.decorator.curr_ns()
                self.decorator.ns(namespace)
                rst = rfc(*a,**b)
                self.decorator.fcns(namespace, rst)
                self.decorator.ns(ns)
                return rst
        return wfc
    def call(self, namespace):
        fcs = self.decorator.fcs
        obj = Fcs(namespace, self)
        for k,f in fcs.items():
            setattr(obj, k, self.fc(namespace, f))
        def wfc(rfc, *a, **b):
            with self.lock:
                ns = self.decorator.curr_ns()
                self.decorator.ns(namespace)
                rst = rfc(*a,**b)
                self.decorator.fcns(namespace, rst)
                self.decorator.ns(ns)
                return rst
        setattr(obj, "wrap", wfc)
        return obj

pass
ns = NameSpace(decorator)
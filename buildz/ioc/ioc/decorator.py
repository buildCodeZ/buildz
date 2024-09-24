#coding=utf-8
from buildz.base import Base
from buildz import xf
class Decorator(Base):
    def init(self):
        self.conf = {}
        self.fcs = {}
        self.regist("add_datas", self.add_datas)
    def regist(self, key, fc):
        self.fcs[key] = fc
    def get(self, tag, index):
        if tag not in self.conf:
            self.conf[tag]=[]
        return self.conf[tag][index]
    def add(self, tag, data):
        if tag not in self.conf:
            self.conf[tag]=[]
        id = len(self.conf[tag])
        self.conf[tag].append(data)
        return id
    def set(self, tag, key, val):
        if tag not in self.conf:
            self.conf[tag]={}
        self.conf[tag][key]=val
    def add_datas(self, item):
        if type(item)==str:
            item = xf.loads(item)
        return self.add("datas", item)
    def get_datas(self, id):
        return self.get("datas", id)
    def set_datas(self, id, val):
        return self.set("datas", id, val)
    def set_envs(self, key, val):
        return self.set("env", key, val)
    def add_inits(self, val):
        return self.add("inits", val)
    def add_locals(self, item):
        return self.add("locals", item)
    def call(self):
        return self.conf

pass

decorator = Decorator()
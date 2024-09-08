#coding=utf-8
from buildz.base import Base
class Decorator(Base):
    def init(self):
        self.conf = {}
        self.fcs = {}
    def regist(self, key, fc):
        self.fcs[key] = fc
    def add(self, tag, data):
        if tag not in self.conf:
            self.conf[tag]=[]
        self.conf[tag].append(data)
    def set(self, tag, key, val):
        if tag not in self.conf:
            self.conf[tag]={}
        self.conf[tag][key]=val
    def add_datas(self, item):
        return self.add("datas", item)
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
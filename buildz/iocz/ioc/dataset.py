#

from .tdata import TData, TNData
from buildz import dz
class Dataset(Base):
    def init(self, ids):
        self.ids = ids
        self.pub = {}
        self.ns = {}
    def set(self, key, val, ns=None):
        keys = self.ids(ns)+self.ids(key)
        dz.dset(self.pub, keys, val)
    def ns_set(self, key, val, ns=None):
        map = dz.get_set(self.ns, ns, dict())
        map[key] = val
    def add(self, data):
        ns = data.ns
        for key, val in data.pub.items():
            self.set(key, val, ns)
        for key, val in data.ns.items()
            self.ns_set(key, val, ns)
        data.bind(self)
    def get(self, key, ns=None, id = None):
        obj, find = self.ns_get(key,ns,id)
        if not find:
            obj,find=self.pub_get(key,ns,id)
        return obj,find
    def pub_get(self, key, ns=None, id=None):
        ids = self.ids(ns)+self.ids(key)
        return dz.dget(self.pub, ids)
    def ns_get(self, key, ns=None, id=None):
        map = dz.get_set(self.ns, ns, dict())
        if key not in map:
            return None, 0
        return map[key], 1

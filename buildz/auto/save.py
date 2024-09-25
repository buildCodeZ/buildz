#
from ..tools import *
from buildz.ioc import wrap
@wrap.obj(id="save")
@wrap.obj_args("ref, cache", "ref, log", "ref, cache.modify")
class Save(Base):
    def init(self, cache, log, upd):
        self.cache = cache
        self.log = log
        self.upd = upd
    def call(self, data, fc=None):
        data = self.upd(data)
        save = xf.g(data, save={})
        for k, v in save.items():
            if type(v)==str:
                v = ["key"]+v.split(".")
            if type(v)!=list:
                v = ["key", v]
            tp = v[0]
            v = v[1:]
            if tp=="eval":
                val = eval(v[0])
            elif tp == "exec":
                exec(v[0])
                val = self.val
            else:
                val = xf.gets(data, v)
            self.cache.set(k, val)
        return True

pass



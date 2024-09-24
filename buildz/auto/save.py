#
from ..tools import *
from buildz.ioc import wrap
@wrap.obj(id="save")
@wrap.obj_args("ref, cache", "ref, log", "ref, cache_modify")
class Save(Base):
    def init(self, cache, log, upd):
        self.cache = cache
        self.log = log
        self.upd = upd
    def call(self, data, fc=None):
        data = self.upd(data)
        save = xf.g(data, save={})
        for k, v in save.items():
            val = xf.gets(data, v.split("."))
            self.cache.set(k, val)
        return True

pass



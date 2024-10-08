#
from ..tools import *
from buildz.ioc import wrap
import os
from buildz.db.dv import build
@wrap.obj(id="dbs")
@wrap.obj_args("ref, cache", "ref, log")
class Dbs(Base):
    def init(self, cache, log):
        self.cache = cache
        self.log = log
        self.dbs = {}
    def call(self, maps, fp):
        confs = xf.g(maps, dbs={})
        for key,conf in confs.items():
            url,user,pwd,dv = xf.g(conf, url=None, user=None, pwd=None, device=key)
            dv = build(dv, [url, user, pwd], val)
            self.dbs[key] = dv
        self.cache.set_mem("dbs", self.dbs)
        return True

pass



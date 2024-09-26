#

from .. import xf, fz
from .. import ioc
from ..base import Base
from ..ioc import wrap
import os,re

@wrap.obj(id="cache.modify")
@wrap.obj_args("ref, cache", "ref, log")
class Update(Base):
    """
    #{}
    """
    def init(self, cache, log, pt = "(#\{([^\{\}]*)\})"):
        self.cache = cache
        self.log = log
        self.pt = pt
    def call(self, s):
        if type(s)==dict:
            rst = {}
            for k,v in s.items():
                k,v = self(k), self(v)
                rst[k] = v
            return rst
        elif type(s)==list:
            rst = []
            for v in s:
                v = self(v)
                rst.append(v)
            return rst
        elif type(s)!=str:
            return s
        rst = re.findall(self.pt, s)
        for match, key in rst:
            val = self.cache.get(key)
            if val is None:
                err = f"'{key}' not found in cache"
                self.log.error(err)
                raise Exception(err)
            if s == match:
                s = val
            else:
                s = s.replace(match, str(val))
        return s

pass



@wrap.obj(id="cache.save")
@wrap.obj_args("ref, cache", "ref, log")
class Save(Base):
    def init(self, cache, log):
        self.cache = cache
        self.log = log
    def call(self, maps, fp):
        fp = xf.get(maps, "cache.save", None)
        if fp is None:
            self.log.warn(f"cache not save cause 'cache.save' is None")
            return
        fz.makefdir(fp)
        rst  = self.cache.data
        rs = xf.dumps(rst, format=True).encode("utf-8")
        fz.write(rs, fp, 'wb')
        return True

pass
@wrap.obj(id="cache")
@wrap.obj_args("ref, log", "env, cache.rfp.current.first, false")
class Cache(Base):
    def get(self, key):
        ks = key.split(".")
        return xf.gets(self.data, ks)
    def set(self, key, val):
        xf.sets(self.data, key.split("."), val)
    def remove(self, key):
        xf.removes(self.data, key.split("."))
    def init(self, log, current_first=False):
        self.current_first = current_first
        self.log = log
        self.data = {}
    def set_current(self, dp):
        if type(dp)!=list:
            dp = [dp]
        self.set("cache.path.current", dp)
    def add_current(self, dp):
        dps = self.get_current()
        if dps is None:
            dps = []
        if dp in dps:
            return
        dps.append(dp)
        self.set_current(dps)
    def get_current(self):
        dps = self.get("cache.path.current")
        if type(dps)!=list:
            dps = [dps]
        return dps
    def rfp(self, fp):
        dps = [None,"."]
        cfps = self.get_current()
        if cfps is not None:
            if self.current_first:
                dps = cfps+dps
            else:
                dps = dps+cfps
        for dp in dps:
            _fp = fp
            if dp is not None:
                _fp = os.path.join(dp, fp)
            if os.path.isfile(_fp):
                return _fp
        return fp
    def call(self, maps, fp):
        fp = xf.g(maps, cache="cache.js")
        data = {}
        if os.path.isfile(fp):
            self.log.info(f"load cache from {fp}")
            data = xf.flush_maps(xf.loadf(fp),visit_list=True)
        xf.fill(data, self.data, replace=0)
        return True

pass

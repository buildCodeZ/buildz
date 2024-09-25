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
        self.log.debug(f"try save cache to '{fp}'")
        if fp is None:
            return
        fz.makefdir(fp)
        rst  = self.cache.data
        rs = xf.dumps(rst, format=True)
        fz.write(rs, fp, 'w')
        return True

pass
@wrap.obj(id="cache")
@wrap.obj_args("ref, log")
class Cache(Base):
    def get(self, key):
        ks = key.split(".")
        return xf.gets(self.data, ks)
    def set(self, key, val):
        xf.sets(self.data, key.split("."), val)
    def remove(self, key):
        xf.removes(self.data, key.split("."))
    def init(self, log):
        self.log = log
        self.data = {}
    def call(self, maps, fp):
        fp = xf.g(maps, cache="cache.js")
        data = {}
        if os.path.isfile(fp):
            self.log.info(f"load cache from {fp}")
            data = xf.flush_maps(xf.loadf(fp),visit_list=False)
        self.data.update(data)
        return True

pass

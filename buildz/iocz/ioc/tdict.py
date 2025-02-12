#
from buildz import pyz,dz,Base
class TDict(Base):
    def remove(self, key, tag=None):
        tag = pyz.nnull(tag, self.default)
        rst = dz.get_set(self.maps, tag, dict())
        dz.dremove(rst, key)
    def set(self, key, val, tag=None):
        tag = pyz.nnull(tag, self.default)
        rst = dz.get_set(self.maps, tag, dict())
        dz.dset(rst, key, val)
    def get(self, key, tags=None):
        if tags is None:
            tags = self.maps.keys()
        elif type(tags) not in (list,tuple,set):
            tags = [tags]
        for tag in tags:
            if tag not in self.maps:
                continue
            rst = self.maps[tag]
            val, has = dz.dget(rst, key)
            if has:
                return val, 1
        return None,0
    def __getattr__(self, tag):
        rst = dz.get_set(self.maps, tag, dict())
        return rst
    def init(self, default=""):
        self.maps = {}
        self.default=default

pass
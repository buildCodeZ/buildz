#
from .datas import Datas
from .dataset import Dataset
from .confs import Confs
class Envs(Datas):
    def init(self, ns=None, id=None, dts=None):
        super().init(ns, id, dts)
        self.ids = None
    def update(self, maps, tag=None, flush=False):
        if flush:
            maps = dz.unflush_maps(maps, self.ids.id)
        for key, val in maps.items():
            self.set(key, val, tag)
    def bind(self, dts):
        self.ids = dts.ids
        super().bind(dts)
    def set(self, key, val, tag=None):
        super().set(self.ids(key), val, tag)
    def get(self, key, tags=None):
        return super().get(self.ids(key), tags)
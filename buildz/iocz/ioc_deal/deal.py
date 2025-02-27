
from .base import *
from ... import dz,pyz
from ..ioc.single import Single
class DealEncape(BaseEncape):
    def init(self, src, targets, tag, prev_call, unit):
        super().init()
        self.src, self.targets, self.tag, self.prev_call, self.unit = src, targets, tag, prev_call, unit
    def call(self, params=None, **maps):
        src = self.src
        if self.prev_call:
            src = src()
        for target in self.targets:
            self.unit.set_deal(target, src, self.tag)
class DealDeal(BaseDeal):
    def init(self):
        super().init()
        self.load_srcs = {}
    def deal(self, conf, unit):
        id,id_find = unit.conf_key(conf)
        src, tag, prev_call = dz.g(conf, source=None, tag=None, call=False)
        targets = dz.g(conf, deals=[])
        if type(targets) not in (list, tuple):
            targets = [targets]
        if Confs.is_conf(src):
            src = unit.get_encape(src, unit)
        elif type(src)==str:
            if src not in self.load_srcs:
                self.load_srcs[src] = pyz.load(src)
            src = self.load_srcs[src]
        return DealEncape(src, targets, tag, prev_call, unit,)

pass
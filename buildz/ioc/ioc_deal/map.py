#coding=utf-8
from ..ioc.base import Base, EncapeData
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class MapDeal(BaseDeal):
    def init(self, fp_lists=None, fp_defaults=None):
        super().init("MapDeal", fp_lists, fp_defaults, join(dp, "conf", "map_lists.js"), None)
    def deal(self, edata:EncapeData):
        data = edata.data
        conf = edata.conf
        data = self.fill(data)
        maps = xf.g(data, data={})
        rst = {k:self.get_obj(map[k], conf) for k in maps}
        return rst

pass

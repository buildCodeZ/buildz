#coding=utf-8
from ..ioc.base import Base, EncapeData
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class IOCObjectDeal(BaseDeal):
    def init(self, fp_lists=None, fp_defaults=None):
        super().init("IOCObjectDeal", fp_lists, fp_defaults, join(dp, "conf", "ioc_lists.js"), None)
    def deal(self, edata:EncapeData):
        data = edata.data
        data = self.fill(data)
        key = data['key']
        if not hasattr(edata, key):
            return None
        return getattr(edata, key)

pass

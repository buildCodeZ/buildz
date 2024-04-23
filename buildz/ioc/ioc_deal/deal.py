#coding=utf-8
from ..ioc.base import Base, EncapeData,IOCError
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class DealDeal(BaseDeal):
    """
        // 调用后会注册到conf的deal上，用于扩展deals配置
        deal字段deal:
            {
                id:id
                type: deal
                target: type
                source: id # 要求source实现了方法__call__(self, edata:EncapeData)
            }
        简写:
            [[id, deal], target, source]
            [deal, target, source]
        例:
            [deal, target, source] //
    """
    def init(self, fp_lists=None, fp_defaults=None):
        super().init("DealDeal", fp_lists, fp_defaults, join(dp, "conf", "deal_lists.js"), None)
    def deal(self, edata:EncapeData):
        data = edata.data
        source = xf.g(data, source=None)
        if source is None:
            raise IOCError("not source in dealdeal")
        target = xf.g(data, target=None)
        if target is None:
            raise IOCError("not target in dealdeal")
        obj = edata.conf.get(source)
        if obj is None:
            raise IOCError("source object not found in dealdeal")
        edata.conf.set_deal(target, obj)
        return None

pass

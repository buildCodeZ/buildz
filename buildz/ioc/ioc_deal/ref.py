#coding=utf-8
from ..ioc.base import Base, EncapeData
from .base import FormatData,FormatDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class RefDeal(FormatDeal):
    """
        引用ref:
            {
                id: id
                type: ref
                key: 引导数据id
                info: item_conf, 额外的引用信息, 默认null
            }
        简写:
            [[id, ref], key, info]
        极简:
            [ref, key]
        例:
            [ref, obj.test] // 数据项"obj.test"的引用
    """
    def init(self, fp_lists=None, fp_defaults=None):
        super().init("RefDeal", fp_lists, fp_defaults, join(dp, "conf", "ref_lists.js"), None)
    def deal(self, edata:EncapeData):
        data = edata.data
        data = self.fill(data)
        key = data['key']
        info = xf.g(data, info=None)
        if info is not None:
            info = self.get_obj(info, src = edata.src)
        return edata.conf.get_obj(key, info = info, src = edata.src)

pass

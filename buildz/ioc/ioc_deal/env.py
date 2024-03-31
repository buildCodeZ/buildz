#
from ..ioc.base import Base, EncapeData
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class EnvDeal(BaseDeal):
    def init(self, fp_lists=None, fp_defaults=None):
        super().init("EnvDeal", fp_lists, fp_defaults, join(dp, "conf", "env_lists.js"), None)
    def deal(self, edata:EncapeData):
        data = edata.data
        data = self.fill(data)
        key = data['key']
        return edata.conf.get_env(key)

pass

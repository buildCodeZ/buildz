#
from ..ioc.base import Base, EncapeData
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class EnvDeal(BaseDeal):
    """
        环境变量env:
            {
                id: id
                type: env
                key: 环境变量key
            }
        简写：
            [[id, env], key]
            [env, key]
        例:
            [env, path] //读取环境变量path
    """
    def init(self, fp_lists=None, fp_defaults=None):
        super().init("EnvDeal", fp_lists, fp_defaults, join(dp, "conf", "env_lists.js"), None)
    def deal(self, edata:EncapeData):
        data = edata.data
        data = self.fill(data)
        key = data['key']
        return edata.conf.get_env(key)

pass

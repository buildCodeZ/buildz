#
from ..ioc.base import Base, EncapeData
from .base import FormatData,FormatDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class VarDeal(FormatDeal):
    """
        代码变量var:
            {
                id:id
                type: var
                var|data: string
            }
        简写:
            [[id, var], data]
            [var, data]
        例:
            [var, buildz.pyz.is_windows] // 返回buildz.pyz下的is_windows
    """
    def init(self, fp_lists = None, fp_defaults = None):
        self.singles = {}
        self.sources = {}
        super().init("VarDeal", fp_lists, fp_defaults, 
            join(dp, "conf", "var_lists.js"))
    def deal(self, edata:EncapeData):
        sid = edata.sid
        data = edata.data
        conf = edata.conf
        data = self.format(data)
        src = edata.src
        key = xf.get_first(data, "var", "data")
        key = pyz.load(key)
        return key

pass

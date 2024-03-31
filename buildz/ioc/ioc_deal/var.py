#
from ..ioc.base import Base, EncapeData
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class VarDeal(BaseDeal):
    """
    {
        id: ...
        type: ovar
        source: 
        method: 
    }
    [[id, type], source, method]
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
        key = xf.g(data, key=0)
        key = pyz.load(key)
        return key

pass

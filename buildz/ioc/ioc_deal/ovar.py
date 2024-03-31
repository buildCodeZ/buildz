#
from ..ioc.base import Base, EncapeData
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class ObjectVarDeal(BaseDeal):
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
        super().init("ObjectVarDeal", fp_lists, fp_defaults, 
            join(dp, "conf", "ovar_lists.js"))
    def deal(self, edata:EncapeData):
        sid = edata.sid
        data = edata.data
        conf = edata.conf
        data = self.format(data)
        src = edata.src
        source = xf.g(data, source=None)
        key = xf.g(data, key=0)
        if source is not None:
            source = conf.get(source)
        if source is None:
            source = src
        if source is None:
            raise Exception(f"not object for key {key}")
        key = getattr(source, key)
        return key

pass

#
from ..ioc.base import Base, EncapeData
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class MethodCallDeal(BaseDeal):
    """
    {
        id: ...
        type: mcall
        source: 
        method: 
        args: []
        maps: {}
    }
    [[id, mcall], source, method, args, maps]
    """
    def init(self, fp_lists = None, fp_defaults = None):
        self.singles = {}
        self.sources = {}
        super().init("MethodCallDeal", fp_lists, fp_defaults, 
            join(dp, "conf", "mcall_lists.js"),
            join(dp, "conf", "mcall_defaults.js"))
    def deal(self, edata:EncapeData):
        sid = edata.sid
        data = edata.data
        conf = edata.conf
        data = self.format(data)
        src = edata.src
        source = xf.g(data, source=None)
        method = xf.g(data, method=0)
        if source is not None:
            source = conf.get(source)
        if source is None:
            source = src
        if source is None:
            raise Exception(f"not object for method {method}")
        if src is None:
            src = source
        method = getattr(source, method)
        args = xf.g(data, args=[])
        maps = xf.g(data, maps ={})
        args = [self.get_obj(v, conf, src) for v in args]
        maps = {k:self.get_obj(maps[k], conf, src) for k in maps}
        return method(*args, **maps)

pass

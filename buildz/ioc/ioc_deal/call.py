#
from ..ioc.base import Base, EncapeData
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class CallDeal(BaseDeal):
    """
    {
        id: ...
        type: call
        method: 
        args: []
        maps: {}
    }
    [[id, type], method, args, maps]
    """
    def init(self, fp_lists = None, fp_defaults = None):
        self.singles = {}
        self.sources = {}
        super().init("CallDeal", fp_lists, fp_defaults, 
            join(dp, "conf", "call_lists.js"),
            join(dp, "conf", "call_defaults.js"))
    def deal(self, edata:EncapeData):
        sid = edata.sid
        data = edata.data
        conf = edata.conf
        data = self.format(data)
        src = edata.src
        method = xf.g(data, method=0)
        method = pyz.load(method)
        args = xf.g(data, args=[])
        maps = xf.g(data, maps ={})
        args = [self.get_obj(v, conf, src) for v in args]
        maps = {k:self.get_obj(maps[k], conf, src) for k in maps}
        return method(*args, **maps)

pass

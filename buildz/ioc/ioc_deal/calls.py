#
from ..ioc.base import Base, EncapeData
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class CallsDeal(BaseDeal):
    """
    {
        id: ...
        type: calls
        calls: [
            ...
        ]
    }
    [[id, type], calls]
    """
    def init(self, fp_lists = None, fp_defaults = None):
        self.singles = {}
        self.sources = {}
        super().init("CallsDeal", fp_lists, fp_defaults, 
            join(dp, "conf", "calls_lists.js"),
            join(dp, "conf", "calls_defaults.js"))
    def deal(self, edata:EncapeData):
        sid = edata.sid
        data = edata.data
        conf = edata.conf
        data = self.format(data)
        src = edata.src
        calls = xf.g(data, calls=[])
        for call in calls:
            rst = self.get_obj(call, conf, src)
        return rst

pass

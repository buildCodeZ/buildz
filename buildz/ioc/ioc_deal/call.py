#
from ..ioc.base import Base, EncapeData
from .base import FormatData,FormatDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class CallDeal(FormatDeal):
    """
    函数调用call:
        {
            id:id
            type:call
            method: import路径+"."+方法名
            args: [item_conf, ...]
            maps: {
                key1:item_conf,
                ...
            }
        }
    简写:
        [[id, call], method, args, maps]
        [call, method]
    例:
        [call, buildz.ioc.demo.test.test] //调用buildz.ioc.demo.test下的test方法
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
        info = edata.info
        iargs, imaps = None, None
        if type(info) == dict:
            iargs, imaps = xf.g(info, args = None, maps = None)
        args = xf.g(data, args=[])
        maps = xf.g(data, maps ={})
        if iargs is not None:
            args = iargs
        if imaps is not None:
            xf.fill(imaps, maps, 1)
        # args = [self.get_obj(v, conf, src, info = edata.info) for v in args]
        # maps = {k:self.get_obj(maps[k], conf, src, info = edata.info) for k in maps}
        args = [self.get_obj(v, conf, src) for v in args]
        maps = {k:self.get_obj(maps[k], conf, src) for k in maps}
        return method(*args, **maps)

pass

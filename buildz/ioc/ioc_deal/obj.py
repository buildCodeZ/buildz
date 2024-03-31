#
from ..ioc.base import Base, EncapeData
from .base import FormatData,BaseDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class ObjectDeal(BaseDeal):
    """
    {
        id: ...
        type: object
        single: 1
        source: 
        construct: {
            args: []
            maps: {
            }
        }
        sets: [
            {key: ..., val: {...}}
        ]
    }
    """
    def init(self, fp_lists = None, fp_defaults = None, fp_cst = None, fp_set = None):
        self.singles = {}
        self.sources = {}
        super().init("ObjectDeal", fp_lists, fp_defaults, 
            join(dp, "conf", "obj_lists.js"),
            join(dp, "conf", "obj_defaults.js"))
        if fp_set is None:
            fp_set = join(dp, 'conf', 'obj_set_lists.js')
        if fp_cst is None:
            fp_cst = join(dp, 'conf', 'obj_cst_lists.js')
        self.fmt_set = FormatData(xf.loads(xf.fread(fp_set)))
        self.fmt_cst = FormatData(xf.loads(xf.fread(fp_cst)))
    def get_maps(self, maps, sid, id):
        if id is None:
            return None
        if sid not in maps:
            return None
        maps = maps[sid]
        if id not in maps:
            return None
        return maps[id]
    def set_maps(self, maps, sid, id, obj):
        if sid not in maps:
            maps[sid] = {}
        maps[sid][id] = obj
    def deal(self, edata:EncapeData):
        sid = edata.sid
        data = edata.data
        data = self.format(data)
        id = xf.g(data, id = None)
        single = xf.g(data, single=None)
        if id is None:
            single = 0
        if single is None:
            single = 1
        if single:
            obj = self.get_maps(self.singles, sid, id)
            if obj is not None:
                return obj
        conf = edata.conf
        confs = edata.confs
        source = xf.g(data, source=0)
        fc = xf.get(self.sources, source, None)
        if fc is None:
            fc = pyz.load(source)
            self.sources[source]=fc
        cst = xf.g(data, construct = 0)
        cst = self.fmt_cst(cst)
        args = xf.g(cst, args=[])
        maps = xf.g(cst, maps={})
        args = [self.get_obj(v, conf) for v in args]
        maps = {k:self.get_obj(maps[k], conf) for k in maps}
        obj = fc(*args, **maps)
        if single:
            self.set_maps(self.singles, sid, id, obj)
        sets = xf.g(data, sets=[])
        for kv in sets:
            kv = self.fmt_set(kv)
            k = kv['key']
            v = kv['val']
            v = self.get_obj(v, conf, obj)
            setattr(obj, k, v)
        calls = xf.g(data, calls=[])
        for call in calls:
            rst = self.get_obj(call, conf, obj)
        return obj

pass

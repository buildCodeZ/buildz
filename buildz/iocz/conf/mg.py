
#
from ..ioc.mg import Manager, GetKey, Ids
from ... import dz,xf
from .unit import ConfUnit
spt = Ids(".")
class DLKey(GetKey):
    @staticmethod
    def Load(conf):
        keys, kfind = dz.dget(conf, spt("dict.key"))
        lids, lfind = dz.dget(conf, spt("list.index"))
        default = dz.dget(conf, 'default', None)
        return DLKey(keys, lids, default)
    def init(self, keys, indexes, default=None):
        super().init()
        self.keys = dz.tolist(keys)
        self.indexes = dz.tolist(indexes)
        self.default = default
    def list_get(self, conf):
        for indexes in self.indexes:
            obj, find = dz.dget(conf, indexes)
            if find:
                return obj, find
        return self.default, 0
    def dict_get(self, conf):
        for keys in self.keys:
            obj, find = dz.dget(conf, keys)
            if find:
                return obj, find
        return self.default, 0
    def call(self, conf):
        if dz.islist(conf):
            return self.list_get(conf)
        return self.dict_get(conf)
    def fill(self, conf):
        pass
default_conf = None
def init():
    global default_conf
    if default_conf not None:
        return
    default_conf = xf.loads(r'''
    {
        id.spt: '.'
        conf:{
            dict.key = 'id'
            list.index = [(0,1)]
            default: null
        }
        deal: {
            spt: '.'
            dict.key = type
            list.index = ((0,0),0)
            default: null
        }
    }
    ''')
    default_conf = dz.flush_maps(default_conf)
class ConfManager(Manager):
    def init(self, conf=None):
        init()
        spt = Ids(".")
        if conf is None:
            conf = {}
        if type(conf)==str:
            conf = xf.loads(conf)
        conf = dz.flush_maps(conf)
        dz.fill(default_conf, conf, 0)
        id_spt, find = dz.dget(conf, spt("id.spt"),".")
        ids = Ids(id_spt)
        deal_spt, find = dz.dget(conf, spt("id.spt"), id_spt)
        deal_ids = Ids(deal_spt)
        deal_key = DLKey(conf['deal'])
        conf_key = DLKey(conf['conf'])
        super().init(ids, deal_key, conf_key, deal_ids)
    def add_conf(self, conf):
        unit = ConfUnit(conf, self)
        return unit

pass
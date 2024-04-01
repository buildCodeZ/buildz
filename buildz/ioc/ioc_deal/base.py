#coding=utf-8

from ..ioc.base import Base, EncapeData
from buildz import xf
import os
dp = os.path.dirname(__file__)
join = os.path.join
default_deals = join(dp, 'conf', 'deals.js')
class FormatData(Base):
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
            {key: ..., val: ..., type: ...}
        ]
    }
    [[id, type, single], source, construct:[args, maps], sets]
    [
        {
            nullable: 0
            out: 1
            //key: construct
            //default: []
            conf: [
                {key: id, default: null}
                {key: type, default: null }
                {key: single, default: 1}
            ]
        }
        {
            nullable: 0
            key: source
        }
        {
            key: construct
            default: {args: [], maps: {}}
            conf: [
                {key: args, default: []}
                {key: maps, default: {}}
            ]
        }
        {
            key: sets
            default: []
        }
    ]
    """
    def init(self, lists = [], defaults = {}, name = "demo"):
        self.lists = lists
        self.defaults = {}
        self.name = name
    def deal(self, data, lists = None, defaults = None):
        data = self.l2m(data, lists)
        data = self.fill(data, defaults)
        return data
    def fill(self, data, defaults = None):
        if defaults is None:
            defaults = self.defaults
        "没有值的时候用默认值填充"
        xf.deep_update(data, self.defaults, replace=0)
        return data
    def l2m(self, data, lists=None):
        if type(data) == dict:
            return data
        if type(data) not in [list, tuple]:
            data = [data]
        if lists is None:
            lists = self.lists
        if type(lists) in [list, tuple]:
            lists = {'sort':1, 'data': lists}
        maps = {}
        i=0
        sort = xf.g(lists, sort=1)
        lists = xf.g(lists, data=[])
        if sort:
            rs = range(len(lists))
        else:
            rs = range(len(lists)-1, -1, -1)
        #for obj in lists:
        cnt = 0
        for i in rs:
            obj = lists[i]
            key = xf.g(obj, key=None)
            out = xf.g(obj, out = 0)
            if not out and key is None:
                raise Exception(f"error format in {self.name}, has not key and not out")
            if cnt>=len(data):
                null = xf.g(obj, nullable=1)
                if not null:
                    raise Exception(f"error format in {self.name}, not default value for index {i}, key {key}")
                default = xf.g(obj, default=None)
                maps[key] = default
                cnt +=1
                continue
            next_conf = xf.g(obj, conf = None)
            #print(f"[TEST CALL] i: {i}, data: {data}, obj: {obj}")
            obj = data[i]
            if next_conf is None:
                maps[key] = obj
                cnt +=1
                continue
            _maps = self.l2m(obj, next_conf)
            if out:
                maps.update(_maps)
            else:
                maps[key] = _maps
            cnt +=1
        return maps

pass


class BaseDeal(Base):
    def init(self, name = "BaseDeal", fp_lists = None, fp_defaults = None, df_fp_lists=None, df_fp_defaults=None):
        self.singles = {}
        self.sources = {}
        if fp_lists is None:
            fp_lists = df_fp_lists
        if fp_defaults is None:
            fp_defaults = df_fp_defaults
        lists = []
        defaults = {}
        if fp_lists  is not None:
            lists = xf.loads(xf.fread(fp_lists))
        if fp_defaults  is not None:
            defaults = xf.loads(xf.fread(fp_defaults))
        self.format = FormatData(lists, defaults, name)
    def fill(self, data):
        data = self.format.l2m(data)
        self.format.fill(data)
        return data
    def get_obj(self, data, conf, src = None):
        type = conf.confs.get_data_type(data, 1, conf.default_type())
        edata = EncapeData(data, conf, local=True, type=type, src = src)
        deal = conf.get_deal(edata.type)
        if deal is None:
            return None
        return deal(edata)
    def deal(self, edata:EncapeData):
        return None

pass
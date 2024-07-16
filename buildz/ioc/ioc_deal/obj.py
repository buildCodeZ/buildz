#
from ..ioc.base import Base, EncapeData,IOCError
from .base import FormatData,FormatDeal
from buildz import xf, pyz
import os
dp = os.path.dirname(__file__)
join = os.path.join
class ObjectDeal(FormatDeal):
    """
        对象object:
            {
                id: id
                type: object
                source: 导入路径+调用方法/类
                single: 1 //是否单例，默认是，
                        //这里的单例是一个id对应一个实例，
                        //如果两个id用的同一个source，就是同一个source的两个对象
                // 构造函数
                construct:{
                    args: [
                        item_conf,
                        ...
                    ]
                    maps: {
                        key1: item_conf,
                        ...
                    }
                }
                //construct和args+maps，不能同时存在
                args: [
                    item_conf,
                    ...
                ]
                maps: {
                    key1: item_conf,
                    ...
                }
                // sets之前调用方法
                prev_call: item_conf
                // 对象变量设置属性
                sets: [
                    {key: key1, data: item_conf }
                    ...
                ]
                // sets之后调用
                call: item_conf
                // remove前调用
                remove: item_conf
                // remove后调用
                after_remove: item_conf
            }
        简写：
            [[id, object, single], source, args, maps, sets, calls] 
                sets: [[key1, item_conf], ...]
        极简:
            [object, source]
        例:
            [object, buildz.ioc.ioc.conf.Conf] //生成Conf对象
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
    def _deal(self, edata:EncapeData):
        sid = edata.sid
        data = edata.data
        data = self.format(data)
        info = edata.info
        conf = edata.conf
        confs = edata.confs
        icst = None
        isets = None
        ivars = None
        if type(info) == dict:
            cid = xf.g(info, id=None)
            iargs, imaps = xf.g(info, args = None, maps = None)
            icst = {'args':iargs, 'maps':imaps}
            isets = xf.g(info, sets = None)
            ivars = xf.g(info, vars=None)
        else:
            cid = None
        id = xf.g(data, id = None)
        single = xf.g(data, single=None)
        if id is None:
            single = 0
        if single is None:
            single = 1
        ids = None
        if single or cid is not None:
            if cid is not None:
                ids = [sid, 'local_id', id, cid]
            else:
                if icst is not None or isets is not None:
                    raise Exception("set info.construct/info.sets while using single without info.id")
                ids = [sid, 'single', id]
        #print(f"obj.deal ids: {ids} for {data}")
        if ids is not None:
            obj = xf.gets(self.singles, ids)
            if obj is not None:
                #raise IOCError(f"null for {ids}")
                return obj
        #source = xf.g(data, source=0)
        source = xf.g1(data, source=0, src=0)
        if source == 0:
            raise Exception(f"define object without 'source' key, {data}")
        source = self.get_obj(source, conf)
        if type(source)==str:
            fc = xf.get(self.sources, source, None)
        else:
            fc = source
        if fc is None:
            fc = pyz.load(source)
            self.sources[source]=fc
        cst = xf.g(data, construct = None)
        if cst is None:
            _args = xf.g(data, args = [])
            _maps = xf.g(data, maps = {})
            cst = [_args, _maps]
        cst = self.fmt_cst(cst)
        if icst is not None:
            xf.fill(icst, cst, 1)
        args = xf.g(cst, args=[])
        maps = xf.g(cst, maps={})
        args = [self.get_obj(v, conf) for v in args]
        maps = {k:self.get_obj(maps[k], conf) for k in maps}
        self.push_vars(conf, ivars)
        obj = fc(*args, **maps)
        if ids is not None:
            xf.sets(self.singles, ids, obj)
        prev_call = xf.g(data, prev_call=None)
        if prev_call is not None:
            # TODO: 这边info透传不知道会不会有问题
            self.get_obj(prev_call, conf, obj, edata.info)
        sets = xf.g(data, sets=[])
        if type(sets)==list:
            tmp = {}
            for kv in sets:
                kv = self.fmt_set(kv)
                k = kv['key']
                v = xf.get_first(kv, "val", "data")
                tmp[k] = v
            sets = tmp
        if type(isets) == list:
            tmp = {}
            for kv in isets:
                kv = self.fmt_set(kv)
                k = kv['key']
                v = xf.get_first(kv, "val", "data")
                tmp[k] = v
            isets = tmp
        if isets is not None:
            xf.fill(isets, sets, 1)
        for k,v in sets.items():
            v = self.get_obj(v, conf, obj)#, edata.info)
            setattr(obj, k, v)
        call = xf.g(data, call=None)
        if call is not None:
            self.get_obj(call, conf, obj)#, edata.info)
        self.pop_vars(conf, ivars)
        #print(f"obj.deal ids: {ids} for {data}, rst: {obj}")
        return obj
    def remove(self, edata:EncapeData):
        sid = edata.sid
        data = edata.data
        data = self.format(data)
        info = edata.info
        conf = edata.conf
        confs = edata.confs
        if type(info) == dict:
            cid = xf.g(info, id=None)
        else:
            cid = None
        id = xf.g(data, id = None)
        single = xf.g(data, single=None)
        if id is None:
            single = 0
        ids = None
        if single or cid is not None:
            if single:
                ids = [sid, id]
            else:
                ids = [sid, id, cid]
        if ids is None:
            return None
        obj = xf.gets(self.singles, ids)
        if obj is None:
            return None
        call = xf.g(data, remove=None)
        if call is not None:
            self.get_obj(call, conf, obj, edata.info)
        xf.removes(self.singles, ids)
        call = xf.g(data, after_remove=None)
        if call is not None:
            self.get_obj(call, conf, obj, edata.info)
        return None

pass

#coding=utf-8
from buildz import xf, pyz
from buildz.xf import g as xg
import json
from .base import Base, EncapeData,IOCError
from builtins import id as _id
class Conf(Base):
    """
        配置文件格式：
            {
                id: 配置文件id，默认null
                //在配置文件配置的环境变量
                envs: {
                    id: val
                    ...
                }
                // 数据配置项处理逻辑，一般不用管
                deals: {
                    {
                        type: 要处理的数据类型
                        build: 函数import的路径
                        args: [] // 列表入参
                        maps: {} // 字典入参
                    }
                }
                namespace: 命名空间，默认null
                //本地数据配置项
                locals: [
                    item_conf,
                    ...
                ]
                //全局数据配置项
                datas: [
                    item_conf,
                    ...
                ]
                // 初始化，会一个一个get(id)
                // 其他地方调用该conf.get的时候，会先判断有没有进行init，没有就先调init里的get
                inits: [
                    id,
                    ...
                ]
            }
        如果只有全局数据配置项，可以只写datas里的东西:
            [
                //全局数据配置项
                item_conf,
                ...
            ]
    """
    def get_key(self, obj, key = 'id', index=0):
        if type(obj)==dict:
            return obj[key]
        id = obj[index]
        if type(id) in [list, tuple]:
            return id[0]
        return id
    def map(self, arr, fc_key):
        return {fc_key(obj): obj for obj in arr}
    def init(self, conf, confs):
        """
            {
                deals:[{build: fc_path,args: [],maps: {}}]
                envs: {id: val}
                id: default null
                namespace: default null
                datas: [{id:val, type: val, ...}]
                locals: [like datas]
                default_type: default null
            }
        """
        if type(conf)!=dict:
            conf = {'datas':conf}
        id = xf.g(conf, id=None)
        if id is None:
            id = confs.conf_id()
        self.id = id
        self.namespace = xf.g(conf, namespace=None)
        self.conf = conf
        self.confs = confs
        self.locals = self.map(xf.g(conf, locals=[]), self.confs.get_data_id)
        self.datas = self.map(xf.g(conf, datas=[]), self.confs.get_data_id)
        self.deals = self.map(xf.g(conf, deals = []), self.confs.get_deal_type)
        self.inits = xf.g(conf, inits = [])
        self._default_type = xf.g(conf, default_type = None)
        self.envs = xf.g(conf, envs = {})
        self.confs.flush_env(self.envs)
        self.confs.update_env(self.envs)
        for _type in list(self.deals.keys()):
            conf = self.deals[_type]
            if type(conf) in [list, tuple]:
                maps = {}
                maps['type'] = conf[0]
                maps['build'] = conf[1]
                arr = conf[2:]
                if len(arr)>0:
                    maps['args'] = arr.pop(0)
                if len(arr)>0:
                    maps['maps'] = arr.pop(0)
                conf = maps
            fc = pyz.load(conf["build"])
            args = xf.g(conf, args=[])
            maps = xf.g(conf, maps={})
            deal = fc(*args, **maps)
            self.deals[_type] = deal
            aliases = xf.g(conf, aliases = [])
            for alias in aliases:
                self.deals[alias] = deal
        self.mark_init = False
    def do_init(self):
        if self.mark_init:
            return
        self.mark_init = True
        for id in self.inits:
            self.get(id)
    def get_env(self, id, search_confs = True):
        if self.confs.global_env and search_confs:
            return self.confs.get_env(id, self.id)
        envs = self.confs.get_env_maps(id, self.envs)
        if envs is not None:
            return envs
        if not search_confs:
            return None
        return self.confs.get_env(id, self.id)
    def set_deal(self, type, fc):
        self.deals[type] = fc
        self.confs.set_deal(type, fc)
    def get_deal(self, type, search_confs = True):
        if self.confs.global_deal and search_confs:
            return self.confs.get_deal(type, self.id)
        if type in self.deals:
            return self.deals[type]
        if not search_confs:
            return None
        return self.confs.get_deal(type, self.id)
    def get_data_conf(self, data, src = None, info = None):
        if type(data) not in [list, dict, tuple]:
            i = self.confs.data_index_type[0]
            data = [self.default_type(), data]
            if i != 0:
                data.reverse()
        _type = self.confs.get_data_type(data, 1, self.default_type())
        edata = EncapeData(data, self, local=True, type=_type, src = src, info = info)
        return edata
    def get_data(self, id, local = True, search_confs = True, src = None, info = None):
        self.do_init()
        if type(id) in [list, tuple, dict]:
            return self.get_data_conf(id, src, info)
        if id in self.datas:
            obj = self.datas[id]
            edata = EncapeData(obj, self, local = False, src=src, info = info)
            if _id(obj) != _id(edata.data):
                # 有parent，做了填充，用填充后的替换
                self.datas[id] = edata.data
            return edata
        if not local:
            return None
        if id in self.locals:
            obj = self.locals[id]
            edata = EncapeData(obj, self, local = True, src=src, info = info)
            if _id(obj) != _id(edata.data):
                # 有parent，做了填充，用填充后的替换
                self.locals[id] = edata.data
            return edata
        if not search_confs:
            return None
        return self.confs.get_data(id, self.id, src=src, info = info)
    def get(self, *args, **maps):
        return self.get_obj(*args, **maps)
    def default_type(self):
        if self._default_type is None:
            return self.confs.default_type
        return self._default_type
    def get_obj(self, id, src = None, info=None, remove = False):
        """
            根据data id获取data对象，处理逻辑：根据data id查配置，根据配置的type查deal，返回deal处理过的配置
        """
        self.do_init()
        if type(id) == EncapeData:
            conf = id
        else:
            conf = self.get_data(id, src = src, info = info)
        if conf is None:
            raise IOCError(f"can't find conf of {id}")
            return None
        deal = self.get_deal(conf.type)
        if deal is None:
            raise IOCError(f"can't find deal of {id}, type = {conf.type}")
            return None
        if not remove:
            obj = deal(conf)
        else:
            obj = deal.remove(conf)
        return obj
    def remove(self, id):
        return self.get_obj(id, remove=True)

pass

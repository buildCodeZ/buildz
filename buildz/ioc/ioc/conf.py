#coding=utf-8
from buildz import xf, pyz
from buildz.xf import g as xg
import json
from .base import Base, EncapeData
class Conf(Base):
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
        self._default_type = xf.g(conf, default_type = None)
        self.envs = xf.g(conf, envs = {})
        self.confs.flush_env(self.envs)
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
    def get_env(self, id, search_confs = True):
        if self.confs.global_env and search_confs:
            return self.confs.get_env(id, self.id)
        ids = self.confs.env_ids(id)
        envs = self.envs
        find = None
        for id in ids:
            if type(envs)!=dict:
                envs = None
                break
            if id not in envs:
                envs = None
                break
            envs = envs[id]
        if envs is not None:
            return envs
        if not search_confs:
            return None
        return self.confs.get_env(id, self.id)
    def get_deal(self, type, search_confs = True):
        if self.confs.global_deal and search_confs:
            return self.confs.get_deal(type, self.id)
        if type in self.deals:
            return self.deals[type]
        if not search_confs:
            return None
        return self.confs.get_deal(type, self.id)
    def get_data(self, id, local = True, search_confs = True):
        if id in self.datas:
            obj = self.datas[id]
            return EncapeData(obj, self, local = False)
        if not local:
            return None
        if id in self.locals:
            obj = self.locals[id]
            return EncapeData(obj, self, local = True)
        if not search_confs:
            return None
        return self.confs.get_data(id, self.id)
    def get(self, *args, **maps):
        return self.get_obj(*args, **maps)
    def default_type(self):
        if self._default_type is None:
            return self.confs.default_type
        return self._default_type
    def get_obj(self, id):
        """
            根据data id获取data对象，处理逻辑：根据data id查配置，根据配置的type查deal，返回deal处理过的配置
        """
        conf = self.get_data(id)
        if conf is None:
            return None
        deal = self.get_deal(conf.type)
        if deal is None:
            return None
        return deal(conf)

pass

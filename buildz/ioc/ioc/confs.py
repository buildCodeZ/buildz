#coding=utf-8
from buildz import xf, pyz
from buildz.xf import g as xg
import json
from .base import Base, EncapeData
from .conf import Conf
import os
class ConfsNode(Base):
    def init(self):
        self.confs = []
        self.ids = {}

pass


class Confs(Base):
    """

    """
    def flush_env(self, envs):
        """
            a.b.c:d -> a:{b:{c:d}}
        """
        for key in list(envs.keys()):
            val = envs[key]
            if type(val)==dict:
                self.flush_env(val)
            ids = self.env_ids(key)
            if len(ids)>1:
                del envs[key]
            pids = ids[:-1]
            id = ids[-1]
            tmp = envs
            for pid in pids:
                if pid not in tmp:
                    tmp[pid] = {}
                tmp = tmp[pid]
            if id not in tmp:
                tmp[id] = val
                continue
            tval = tmp[id]
            if type(tval) == dict and type(val)==dict:
                self.update_maps(tval, val)
            else:
                tmp[id] = val
    def env_ids(self, id):
        return id.split(self.env_spt)
    def env_id(self, ids):
        return self.env_spt.join(ids)
    def get_env(self, id, sid=None):
        if sid is not None and not self.global_env:
            val = self.confs[sid].get_env(id, False)
            if val is not None:
                return val
        sysdt = os.getenv(id)
        if sysdt is not None:
            return sysdt
        ids = self.env_ids(id)
        envs = self.envs
        for id in ids:
            if type(envs)!=dict:
                envs = None
                break
            if id not in envs:
                envs = None
                break 
            envs = envs[id]
        return envs
    def set_env(self, id, val):
        obj = {id:val}
        self.flush_env(obj)
        self.update_maps(self.envs, obj)
    def set_deal(self, type, fc):
        self.deals[type] = fc
    def init_fp(self, fp):
        conf = self.loads(xf.fread(fp))
        self.init(conf, self.loads)
    def by_json(self):
        self.by('json')
    def by_xf(self):
        self.by('xf')
    def by(self, type = 'xf'):
        if type == 'xf':
            self.loads = xf.loads
        elif type == 'json':
            self.loads = json.loads
        else:
            raise Exception("only 'xf' and 'json' impl now")
    def get_key(self, obj, key = 'id', index=0):
        if type(obj)==dict:
            return obj[key]
        id = obj[index]
        if type(id) in [list, tuple]:
            return id[0]
        return id
    def init(self, conf={}, loads = None):
        """
        {
            // 环境变量的分隔符
            // default = '.'
            env_spt: .
            // 数据id的分隔符
            // default = "."
            spt: .
            // 数据的默认类型(处理方式)
            // default = 'default'
            default_type: default
            // 全局查id的时候是从最上层开始找还是从最下层开始找（每一层都可能有配置文件）
            // default = false
            deep_first: false
            // true=环境变量env都是全局的（全局查找），否则优先每个配置文件里查环境变量，查不到才查全局
            // default = true
            global_env: true
            // true=类型处理函数deal都是全局的（全局查找），否则优先每个配置文件里查处理函数，查不到才查全局
            // default = true 
            global_deal: true
            // 数据的id字段名
            // default = 'id'
            data_key_id: id
            // 数据的type字段名
            // default = 'type'
            data_key_type: type
            // 数据配置参数是数组的时候，数据id的位置
            // default=[0,0]
            data_index_id: [0,0]
            // 数据配置参数是数组的时候，数据type的位置
            // default=[0,1]
            data_index_type: [0,1]
            // 处理deal的type字段名
            // default = 'type'
            deal_key_type: type
            // deal配置参数是数组的时候，数据type的位置
            // default=0
            deal_index_type: 0
        }
        """
        if loads is None:
            loads = xf.loads
        self.loads = loads
        if type(conf) in [bytes, str]:
            conf = self.loads(conf)
        self.spt = xf.g(conf, spt = ".")
        self.env_spt = xf.g(conf, env_spt = ".")
        self.default_type = xf.g(conf, default_type='default')
        self.deep_first = xf.g(conf, deep_first=False)
        self.global_env = xf.g(conf, global_env = True)
        self.global_deal = xf.g(conf, global_deal = True)
        self.data_key_id = xf.g(conf, data_key_id = 'id')
        self.data_key_type = xf.g(conf, data_key_type = 'type')
        self.data_index_id = xf.g(conf, data_index_id = [0,0])
        self.data_index_type = xf.g(conf, data_index_type = [0,1])
        self.deal_key_type = xf.g(conf, deal_key_type = 'type')
        self.deal_index_type = xf.g(conf, deal_index_type = 0)
        self._conf_id = 0
        self.conf = conf
        self.node = ConfsNode()
        self.confs = {}
        self.deals = {}
        self.envs = {}
    def get_deal_type(self, obj):
        if type(obj)==dict:
            return obj[self.deal_key_type]
        return obj[self.deal_index_type]
    def get_data_id(self, obj):
        if type(obj)==dict:
            return obj[self.data_key_id]
        obj = obj[self.data_index_id[0]]
        if type(obj) in [list, tuple]:
            obj = obj[self.data_index_id[1]]
        return obj
    def get_data_type(self, obj, type_first = 1, default = None):
        if type(obj)==dict:
            if self.data_key_type not in obj:
                return default
            return obj[self.data_key_type]
        obj = obj[self.data_index_type[0]]
        if type(obj) in [list, tuple]:
            return obj[self.data_index_type[1]]
        if type_first:
            return obj
        return default
    def conf_id(self):
        """
            给每个配置文件加一个id，外部不调用
        """
        id = self._conf_id
        self._conf_id+=1
        return id
    def ids(self, id):
        if id is None:
            return []
        """
            data的id转id列表，外部不调用
            例: id = 'a.b.c', spt = ".", ids = ['a','b','c']
        """
        return id.split(self.spt)
    def id(self, ids):
        """
            data的id列表转id，外部不调用
            例: ids = ['a','b','c'], spt = ".", id = 'a.b.c', 
        """
        return self.spt.join(ids)
    def add_fp(self, fp):
        conf = self.loads(xf.fread(fp))
        return self.add(conf)
    def add(self, conf):
        """
            {
                deals:[{build: fc_path,args: [],maps: {}}]
                envs: {id: val}
                id: default null
                namespace: default null
                datas: [{id:val, type: val, ...}]
                locals: [like datas]
            }
        """
        if type(conf) in [bytes, str]:
            conf = self.loads(conf)
        obj = Conf(conf, self)
        id = xf.g(conf, namespace=None)
        ids = self.ids(id)
        node = self.node
        for id in ids:
            if id not in node.ids:
                node.ids[id] = ConfsNode()
            node = node.ids[id]
        node.confs.append(obj)
        self.confs[obj.id] = obj
        for k in obj.deals:
            self.deals[k] = obj.deals[k]
        self.update_maps(self.envs, obj.envs)
    def get(self, *args, **maps):
        return self.get_obj(*args, **maps)
    def get_obj(self, id, sid = None):
        """
            根据data id获取data对象，处理逻辑：根据data id查配置，根据配置的type查deal，返回deal处理过的配置
        """
        conf = self.get_data(id, sid)
        if conf is None:
            return None
        deal = self.get_deal(conf.type, sid)
        if deal is None:
            return None
        #print(f"get_obj: {id}({sid}), conf: {conf}, deal: {deal}, type: {conf.type}")
        return deal(conf)
    def get_deal(self, type, sid=None):
        """
            根据type类型查处理函数deal，sid（配置文件id）不为空并且global_deal=False则先查局部
        """
        if sid is not None and not self.global_deal:
            deal = self.confs[sid].get_deal(type, False)
            if deal is not None:
                return deal
        if type in self.deals:
            return self.deals[type]
        return None
    def get_confs(self, ids):
        """
            根据ids查所有对应的配置文件列表
        """
        node = self.node
        confs = []
        for i in range(len(ids)):
            id = ids[i]
            confs.append([node.confs,i])
            if id not in node.ids:
                break
            node = node.ids[id]
        return confs
    def get_data(self, id, sid=None):
        """
            根据id查对应的data配置
        """
        ids = self.ids(id)
        arr = self.get_confs(ids)
        if self.deep_first:
            arr.reverse()
        for confs,i in arr:
            id = self.id(ids[i:])
            for conf in confs:
                conf = conf.get_data(id, sid==conf.id, False)
                if conf is not None:
                    return conf
        return None

pass

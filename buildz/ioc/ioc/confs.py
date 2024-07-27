#coding=utf-8
from buildz import xf, pyz
from buildz.xf import g as xg
from buildz import argx
import json
from .base import Base, EncapeData,IOCError
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
    def get_env_sys(self, id, sid=None):
        sysdt = os.getenv(id)
        return sysdt
    def build_env_args_xf(self):
        data = xf.args()
        env = data['env']
        self.envs_args = env
        self.flush_env(self.envs_args)
    def build_env_args_buildz(self):
        args, maps = argx.fetch()
        env = maps
        # e = xf.get(maps, e = [])
        # env = xf.get(maps, env=[])
        # env += e
        # env = [k.split("=") for k in env]
        # env = {k[0]:"=".join(k[1:]) for k in env}
        self.envs_args = env
        self.flush_env(self.envs_args)
    def build_env_args(self):
        if self.args_type == "xf":
            self.build_env_args_xf()
        else:
            self.build_env_args_buildz()
    def get_env_args(self, id, sid=None):
        if self.envs_args is None:
            self.build_env_args()
        return self.get_env_maps(id, self.envs_args)
    def get_env_local(self, id, sid=None):
        if sid is not None and not self.global_env:
            val = self.confs[sid].get_env(id, False)
            if val is not None:
                return val
        return None
    def get_env_maps(self, id, maps):
        ids = self.env_ids(id)
        envs = maps
        for id in ids:
            if type(envs)!=dict:
                envs = None
                break
            if id not in envs:
                envs = None
                break 
            envs = envs[id]
        return envs
    def get_env_conf(self, id, sid=None):
        return self.get_env_maps(id, self.envs)
    def get_env(self, id, sid=None):
        for key in self.env_orders:
            fc = self.env_fcs[key]
            obj = fc(id, sid)
            if obj is not None:
                return obj
        return None
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
    def update_env(self, obj):
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
            // 环境变量读取顺序，默认先命令行配置，然后系统变量，然后本地配置文件配置(设置全局则不查)，最后配置文件配置，不想读哪个把哪个删了就可以
            // 命令行配置格式:
            //     -e a=b --env=a=b --env=c=d
            //     env: {a=b, c=d}
            env_orders: [args, sys, local, conf]
            // 命令行读取方式：默认xf(xf.args),可选: buildz(buidlz.argx)
            args_type: 'xf'
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
            data_index_id: [0,1]
            // 数据配置参数是数组的时候，数据type的位置
            // default=[0,1]
            data_index_type: [0,0]
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
        self.data_index_id = xf.g(conf, data_index_id = [0,1])
        self.data_index_type = xf.g(conf, data_index_type = [0,0])
        self.deal_key_type = xf.g(conf, deal_key_type = 'type')
        self.deal_index_type = xf.g(conf, deal_index_type = 0)
        self.env_orders = xf.g(conf, env_orders = ['sys', 'local', 'conf'])
        self.env_fcs = {
            'args': self.get_env_args,
            'sys': self.get_env_sys,
            'local': self.get_env_local,
            'conf': self.get_env_conf
        }
        self.args_type = xf.g(conf, args_type = "xf")
        self._conf_id = 0
        self.conf = conf
        self.node = ConfsNode()
        self.confs = {}
        self.deals = {}
        self.envs = {}
        self.envs_args = None
        self.mark_init = False
        self.vars = {}
        if 'args' in self.env_orders:
            self.build_env_args()
    def get_var(self, key, i=-1):
        if not self.has_var(key):
            return None, False
        return self.vars[key][i], True
    def push_var(self, key, val):
        if key not in self.vars:
            self.vars[key] =  []
        self.vars[key].append(val)
    def has_var(self, key):
        if key not in self.vars:
            return False
        return len(self.vars[key])>0
    def pop_var(self, key):
        if not self.has_var(key):
            return
        self.vars[key].pop(-1)
    def do_init(self):
        if self.mark_init:
            return
        self.mark_init = True
        for id in self.confs:
            self.confs[id].do_init()
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
        self.do_init()
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
    def gid(self, cid, id):
        cids = self.ids(cid)
        ids = self.ids(id)
        return self.id(cids+ids)
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
    def add_fps(self, fps):
        for fp in fps:
            self.add_fp(fp)
    def add_fp(self, fp):
        try:
            conf = self.loads(xf.fread(fp))
            return self.add(conf)
        except:
            print(f'error in loads: {fp}')
            raise
        #return self.add(conf)
    def adds(self, confs):
        for conf in confs:
            self.add(conf)
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
        id = xf.g1(conf, id=None, namespace=None)
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
        self.mark_init = False
    def get(self, *args, **maps):
        return self.get_obj(*args, **maps)
    def remove(self, *a,**b):
        return self.get_obj(*a, **b, remove=True)
    def get_obj(self, id, sid = None, src = None, info = None, remove = False):
        """
            根据data id获取data对象，处理逻辑：根据data id查配置，根据配置的type查deal，返回deal处理过的配置
        """
        self.do_init()
        if type(id) == EncapeData:
            conf = id
        else:
            conf = self.get_data(id, sid, src=src, info = info)
        if conf is None:
            raise IOCError(f"confs: can't find conf of {id}")
            return None
        deal = self.get_deal(conf.type, sid)
        if deal is None:
            raise IOCError(f"confs: can't find deal of {id}, type = {conf.type}")
            return None
        #print(f"get_obj: {id}({sid}), conf: {conf}, deal: {deal}, type: {conf.type}")
        if not remove:
            obj = deal(conf)
        else:
            obj = deal.remove(conf)
        return obj
    def get_deal(self, type, sid=None):
        """
            根据type类型查处理函数deal，sid（配置文件id）不为空并且global_deal=False则先查局部
        """
        self.do_init()
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
    def get_data(self, id, sid=None, src = None, info = None):
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
                _conf = conf.get_data(id, sid==conf.id, False, src = src, info = info)
                if _conf is not None:
                    return _conf
        return None

pass

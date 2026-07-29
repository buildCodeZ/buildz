#
'''
2026/07/23

新的，更简单的buildz._dz.conf

简单的方便读取配置文件的类
没安全措施
每个Conf里有当前的数据conf，和数据是否存在exist
可以执行的操作:
读取，循环读取，修改，删除，修改和删除不会通知其他节点

push和pop操作(耗时高)
push修改当前conf的key
生成修改记录

pop的时候全改回来
因为没用到，暂时不实现，只保留接口和数据

gets可以获取多个key，返回队列
top(domain)回到根节点的domain下
call(domain)到当前节点的domain下，不存在或没有数据就报错

Conf包含数据：
conf: 实际数据
exist: 数据是否存在
domain: 根节点到当前节点的路径字符串
spt,spts: 分割字符串
src: 只读配置，默认为空
root: 根节点



'''

from . import confs as confz
from . import mapz
from buildz import xf
from ..base import Base
import os
def dzkeys(key, spt):
    if key is None:
        return []
    elif type(key)==str:
        if spt is not None:
            key = key.split(spt)
        else:
            key = [key]
    elif type(key) not in (list, tuple):
        key = [key]
    return key

class Conf(confz.Conf):
    def new(self, domain, root, src, conf, exist):
        return Conf(self.spt, self.spts, domain, root, src, conf, exist)
    def lhget(self, key, default=None, loop=-1):
        '''
            循环读取，直到读取到的不是字符串或loop==0或没有对应的key了
        '''
        a,b = self._hget(key, default)
        bak = a, b
        obj = self.root or self
        while b and type(a)==str and loop!=0:
            a,b = obj._hget(a, default)
            if b:
                bak = a,b
            loop-=1
        if loop>0:
            bak = a,b
        return bak
    def key(self, ks):
        return self.spt.join(ks)
    def src_list(self, i, as_conf = True):
        if self.src is None:
            return None
        if self.src.get_type()!=list:
            return None
        if self.src.len()<=i:
            return None
        return self.src.list(i, as_conf)
    def src_hget(self, key, default):
        if self.src is None:
            return default, 0
        return self.src.hget(key, default, loop)
    def src_dm(self, domain):
        if self.src is None:
            return None
        return self.src(domain,0)
    def src_top(self, domain):
        if self.src is None:
            return None
        return self.src.top(domain, 0)
    def lget(self, key, default=None, loop=-1):
        return self.lhget(key, default, loop)[0]
    def hget(self, key, default=None):
        '''
            最基本的读取方法
            先从conf拿，没有则从src拿
        '''
        keys = dzkeys(key, self.spt)
        return super().hget(keys, default)
    def remove(self, key):
        keys = dzkeys(key, self.spt)
        return super().remove(keys)
    def deal_ks(self, keys):
        '''
            一堆key组成的字符串拆分成key的列表
        '''
        keys = dzkeys(keys, self.spts)
        keys = [k.strip() if type(k) == str else k for k in keys]
        return keys
    def set(self, key, val):
        keys = dzkeys(key, self.spt)
        super().set(keys, val)
    def call(self, domain=None, loop=0):
        '''
            获取子域下的数据作为Conf
        '''
        domain = confz.dzkeys(domain)
        return super().call(domain, loop)
    def init(self, spt='.', spts=',', domain=None, root = None, src = None, conf=None, exist=1):
        self.spt = spt
        self.spts = spts
        super().init(domain, root, src, conf, exist)
    def dkey(self, key):
        keys = dzkeys(key, self.spt)
        return super().dkey(key)
    def update(self, conf, flush = 1, replace=1, visit_list=0):
        if flush:
            conf = xf.flush_maps(conf, lambda x:x.split(self.spt) if type(x)==str else [x], visit_list)
        return super().update(conf, replace, visit_list)
    def push(self, key, value, flush = 1, update=0, clean_history = 0):
        if flush and type(value)==dict:
            value = xf.flush_maps(value, lambda x:x.split(self.spt) if type(x)==str else [x], 0)
        keys = dzkeys(key, self.spt)
        return super().push(keys, value, update, clean_history)

pass
maps = xf.loads(r"""
(get,0,1)
(lget,0,1)
(set,1)
(remove)
(push,1)
""")
for item in maps:
    k = item[0]
    ks = k+"s"
    item = item[:1]+[ks]+item[1:]
    Conf.fcs_bind(*item)

pass

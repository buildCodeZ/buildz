'''
2026/07/23
两种逻辑
1，key全局化
2, 一个map里包含另一个map
第2个对于查一个key耗时会更多
但不同map互不相关的时候，会更快

'''

from . import mapz
from buildz import xf
from ..base import Base
import os
def dzkeys(key):
    if key is None:
        return None
    if type(key)==list:
        key = tuple(key)
    if type(key) != tuple:
        key = (key,)
    return key

class Conf(Base):
    def items(self):
        if type(self.conf)==dict:
            rst = self.conf.items()
        else:
            rst = self.conf
        return rst
    def len(self):
        return len(self.conf)
    def items(self, as_conf=True):
        rst = []
        for i in range(self.len()):
            rst.append(self.list(i, as_conf))
        return rst
    def list(self, i, as_conf=True):
        conf = self.conf[i]
        if as_conf:
            domain = self.domain+(i,)
            val = conf
            src = self.src_list(i, as_conf)
            obj = self.root or self
            find = True
            conf = self.new(domain, obj, src, val, find)
        return conf
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
        val, find = default, 0
        keys = dzkeys(key)
        if self.exist and type(self.conf) in (list,dict):
            val, find = mapz.dget(self.conf, keys, default)
        if find:
            return val, find
        return self.src_hget(keys, default)
    def get(self, key, default=None):
        val = self.hget(key, default)[0]
        return val
    def has(self, key):
        return self.hget(key, None)[1]
    def remove(self, key):
        '''
        '''
        if not self.exist or type(self.conf)!=dict:
            return
        keys = dzkeys(key)
        return mapz.dremove(self.conf, keys)
    def deal_ks(self, keys):
        '''
            一堆key组成的字符串拆分成key的列表
        '''
        return keys
    def set(self, key, val):
        keys = dzkeys(key)
        mapz.dset(self.conf, keys, val)
    def append(self, val):
        self.conf.append(val)
    def top(self, domain = None, loop=0):
        '''
            从根目录往下获取子域
        '''
        root = self.root or self
        if domain is not None:
            root = root(domain, loop)
        return root
    def l(self, domain=None, loop=-1):
        return self(domain,loop)
    def call(self, domain=None, loop=0):
        return self.sub(domain, loop)
    def sub(self, domain=None, loop=0):
        '''
            获取子域下的数据作为Conf
        '''
        if domain is None:
            return self.root or self
        domain = dzkeys(domain)
        val,find = self.hget(domain)
        src = self.src_dm(domain)
        if self.domain:
            domain = self.domain+domain
        obj = self.root or self
        bak = domain, val, find, src
        while loop!=0 and find and type(val)==str:
            bak = domain, val, find, src
            val,find = obj.hget(domain)
            src = self.src_top(domain)
            loop-=1
        domain,val,find,src=bak
        return self.new(domain, obj, src, val, find)
    def val(self):
        '''
            返回当前域下的所有数据
        '''
        return self.conf
    def get_type(self):
        return type(self.val())
    def has_val(self):
        return self.exist
    def get_conf(self):
        return self.conf
    def str(self):
        return str(self.get_conf())
    def new(self, domain, root, src, conf, exist):
        return Conf(domain, root, src, conf, exist)
    def init(self, domain=None, root = None, src = None, conf=None, exist=1):
        domain = dzkeys(domain)
        self.domain = domain
        self.root = root
        self.src = src
        if conf is None:
            conf = {}
        self.conf = conf
        self.exist = exist
        self.history = {}
    def clean(self):
        '''
            清空当前数据
        '''
        if self.get_type()!=dict:
            return
        self.history = {}
        for key in self.conf:
            del self.conf[key]
        return self
    def dkey(self, key):
        keys = dzkeys(key)
        if self.domain:
            key = self.domain+key
        return key
    def update(self, conf, flush = 1, replace=1, visit_list=0):
        xf.fill(conf, self.conf, replace=replace)
        return self
    def push(self, key, value, update=0, clean_history = 0):
        if self.get_type()!=dict:
            return None
        keys = dzkeys(key)
        val, find = mapz.dget(self.conf, keys)
        val = mapz.deep_clone(val)
        if clean_history or keys not in self.history:
            self.history[keys] = []
        self.history[keys].append([val, find, update])
        if find and type(value)==dict and type(val)==dict and update:
            self(key).update(value,flush=0)
        else:
            self.set(key, value)
        return key
    def pop(self, key, clean_history = 0):
        key = dzkeys(key)
        if key not in self.history:
            return False
        lst = self.history[key]
        if len(lst)==0:
            return False
        rst = lst.pop(-1)
        if clean_history:
            self.history[key] = []
        if not rst[1]:
            self.remove(key)
            return True
        self.set(key, rst[0])
        return True
    def pops(self, keys, *a, **b):
        keys = self.deal_ks(keys)
        keys.reverse()
        for key in keys:
            self.pop(key)
    def with_push(self, key, *a, **b):
        self.push(key, *a, **b)
        def out():
            self.pop(key)
        return pyz.with_out(out)
    def with_pushs(self, keys, *a, **b):
        self.pushs(keys, *a, **b)
        def out():
            self.pops(keys)
        return pyz.with_out(out)
    def g(self, **maps):
        rst = [self.get(k, v) for k,v in maps.items()]
        if len(rst)==1:
            rst = rst[0]
        return rst
    def s(self, **maps):
        [self.set(k,v) for k,v in maps.items()]
    def has_all(self, keys):
        keys = self.deal_ks(keys)
        rst = [1-self.has(key) for key in keys]
        return sum(rst)==0
    def has_any(self, keys):
        keys = self.deal_ks(keys)
        for key in keys:
            if self.has(key):
                return True
        return False
    @staticmethod
    def fcs_bind(fn, wfn, align=False, null_default= False):
        def wfc(self, keys, *objs, **maps):
            keys = self.deal_ks(keys)
            fc = getattr(self, fn)
            rst = []
            for i in range(len(keys)):
                if i<len(objs):
                    val = fc(keys[i], objs[i], **maps)
                else:
                    if align:
                        raise Exception(f"not val[{i}]")
                    if null_default:
                        val = fc(keys[i], None, **maps)
                    else:
                        val = fc(keys[i], **maps)
                rst.append(val)
            return rst
        setattr(Conf, wfn, wfc)

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


def test():
    conf = Conf()
    conf.set("123", 456)
    conf.set((1,2,3),(4,5,6))
    conf.set(0, [[1,2,3], [4,5]])
    print(f"item: {conf.sub((0,0)).val()}")
    print(f"item: {conf.sub((0,0)).hget(0)}")
    print(f"item: {conf.sub((0,0)).has((0,))}")
    print(f"item: {conf.sub((0,0)).get(1)}")
    print(f"().has(0,0,1): {conf.has((0,0,1))}")
    print(f"(0).has(0,1): {conf(0).has((0,1))}")
    print(f"(0,0).has(1): {conf(0,0).has((1,))}")
    print(f"conf: {conf}")

pass

if __name__=="__main__":
    test()

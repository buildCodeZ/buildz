'''

测试模型的钩子函数调用时间
'''

from . import dv
from .. import az
import torch
from torch import nn
from buildz import log as logz
from buildz.base import Base
from buildz import pyz, dz

class DoneRebuild(Exception):
    pass

pass
class ReCals(Base):
    def clean(self):
        self.base = 0
        self.total_size = 0
        self.recals = []
        self.used = 0
    def init(self, max_size, rebuild = None, rng_dvs = [], cuda_only = False):
        if type(max_size)==str:
            max_size = int(az.nsize(max_size))
        self.max_size = max_size
        self.base = 0
        self.total_size = 0
        self.rebuild = rebuild
        self.rng_dvs = rng_dvs
        self.cuda_only = cuda_only
        self.used = 0
        self.recals = []
    def inc_used(self):
        self.used+=1
        if self.used>=len(self.recals):
            self.clean()
    def call(self, fc, *a, **b):
        return self.forward(self.rng_dvs, fc, *a, **b)
    def forward(self,  rng_dvs, fc, *a, **b):
        recal = ReCal(self, self.rebuild, rng_dvs, self.cuda_only)
        self.recals.append(recal)
        #print(f"curr recals: {len(self.recals)}")
        return recal.forward(fc, *a, *b)
    def add_size(self, size):
        self.total_size+=size
    def check_and_free(self, size, recal=None):
        assert size <= self.max_size, "uncalable case single size is bigger than max_size"
        if self.total_size+size<self.max_size:
            return
        free_size = self.total_size+size-self.max_size
        #print(f"check and do free size: {free_size}")
        if recal is not None:
            free_size = recal.free_size(free_size)
            #print(f"single recal[{id(recal)}] free: {free_size}")
            assert free_size<=0, f"unknown reason that caches can't free a: {free_size}"
            return
        for i in range(self.base, len(self.recals)):
            recal = self.recals[i]
            if recal.total_size>0:
                free_size = recal.free_size(free_size)
                #print(f"recal[{i}/{id(recal)}] free: {free_size}")
                if free_size<=0:
                    if recal.total_size==0:
                        i+=1
                    break
        self.base = i
        assert free_size<=0, f"unknown reason that caches can't free b: {free_size}"
    def cache_size(self):
        size = sum([recal.cache_size() for recal in reacals])
        return size

class ReCal(Base):
    '''
    '''
    def bind_rebuild(self, rebuild):
        self.rebuild = rebuild
    def bind_rng_dvs(self, rng_dvs):
        self.rng_dvs = rng_dvs
    def init(self, recals, rebuild = None, rng_dvs = [], cuda_only = False):
        self.recals = recals
        self.caches = {}
        self.total_size = 0
        self.rebuild = rebuild
        self.abs = -1
        '0: normal, 1: wait_rebuild, 2: done_rebuild'
        self.status = 0 
        self.index=0 
        self.base=0
        self.save_count=0
        self.used = set()
        self.cuda_only = cuda_only
        if type(rng_dvs) in {bool, int}:
            if rng_dvs:
                rng_dvs = [0]
        self.rng_dvs = rng_dvs
        self.rng_states = []
    def get_rngs(self):
        if self.rng_dvs is None:
            return
        # if len(self.rng_dvs)>0:
        #     print(f"get_rngs")
        for i in self.rng_dvs:
            with torch.cuda.device(i):
                self.rng_states.append(torch.cuda.get_rng_state())
    def set_rngs(self):
        if self.rng_dvs is None:
            return
        # if len(self.rng_dvs)>0:
        #     print(f"set_rngs")
        for i, st in zip(self.rng_dvs, self.rng_states):
            with torch.cuda.device(i):
                torch.cuda.set_rng_state(st)
    def forward_init(self, status=0):
        if status == 0:
            self.used = set()
            self.caches = {}
            self.get_rngs()
            self.abs=-1
            self.save_count=0
        else:
            self.set_rngs()
        self.total_size = 0
        self.status = status
        self.index=0 
        self.base=0 
    def call(self, fc, *a, **b):
        return self.forward(fc, *a, **b)
    def forward(self, fc, *a, **b):
        return self.wrap_forward(lambda :fc(*a, **b))
    def wrap_forward(self, fc):
        self.rebuild = fc or self.rebuild
        with self._with_forward(0):
            return self.rebuild()
    def _with_forward(self, status=0):
        obj = torch.autograd.graph.saved_tensors_hooks(self.tensor_save, self.tensor_load)
        def wrap_enter():
            self.forward_init(status)
            obj.__enter__()
        def wrap_out(exc_type, exc_val, exc_tb):
            obj.__exit__(exc_type, exc_val, exc_tb)
        return pyz.With(wrap_enter, wrap_out, True)
    def free_size(self, size):
        cut_size = 0
        cnt=0
        while size>cut_size and len(self.caches)>0:
            _, pop_size = self.caches.pop(self.base)
            cut_size+=pop_size
            self.base+=1
            cnt+=1
        if cut_size>0:
            self.total_size-=cut_size
            self.recals.add_size(-cut_size)
        return size-cut_size
    def tensor_save(self, tuple_data):
        size, is_cuda = dv.sizes_cuda(tuple_data)
        if not is_cuda and self.cuda_only:
            return tuple_data
        if self.status==2 and self.index in self.used:
            raise DoneRebuild()
        recal=None
        if self.status!=0:
            recal = self
        self.recals.check_and_free(size, recal)
        self.caches[self.index] = (tuple_data, size)
        self.recals.add_size(size)
        self.total_size+=size
        if self.index==self.abs:
            self.status = 2
        self.index+=1
        if self.status==0:
            self.save_count+=1
        return self.index-1
    def do_rebuild(self):
        assert self.rebuild is not None, "use bind_rebuild(fc) to set a rebuild function"
        with self._with_forward(1):
            with torch.enable_grad():
                try:
                    self.rebuild()
                except DoneRebuild as exp:
                    pass
    def tensor_load(self, key):
        if type(key)!=int:
            return key
        obj, size = self.caches.pop(key, (None, 0))
        if obj is None:
            self.abs = key
            self.do_rebuild()
            obj, size = self.caches.pop(key)
        self.total_size-=size
        self.recals.add_size(-size)
        self.used.add(key)
        if len(self.used)==self.save_count:
            self.recals.inc_used()
        return obj
    def cache_size(self, fmt=False):
        size = self.total_size
        if fmt:
            size = az.fmt_sz(size)
        return size

def recals_with_rngs(max_size:int, rng_devices:list|str|int|tuple="all",rebuild = None):
    '''
        rng_devices: 
            需要在计算前存储随机数种子的显卡设备，避免在反向梯度计算时重新计算因为网络层运行的随机性导致和之前计算的不不一样（比如dropout）
            取值:
            str: 
                "null", "none": no cuda device
                "all", scan all cuda devices
            int: torch.cuda.device(rng_devices)
            list: [torch.cuda.device(i) for i in rng_devices]
    '''
    if isinstance(rng_devices, torch.Tensor):
        rng_devices = [rng_devices.get_device()]
    elif type(rng_devices)==str:
        assert rng_devices in {"null","none","all"},f"unknown rng_devices str: {rng_devices}, should be 'all' or 'null'"
        if rng_devices=="all":
            rng_devices = list(range(torch.cuda.device_count()))
        else:
            rng_devices = []
    elif type(rng_devices)==int:
        rng_devices = [rng_devices]
    assert type(rng_devices) in {tuple, list}, "rng_devices should be int or str or list or tuple"
    print(f"rng_devices: {rng_devices}")
    return ReCals(max_size, rebuild, rng_devices)



"""#

集合的形式

recals()调用的时候生成一个子对象，
save逻辑修改：
    空间不够的时候，调用主对象的清理指令，或者干脆由主对象判断，主对象判断空间不够按顺序调用子对象的释放函数，直到空间足够，子对象会在自身空间为0或非0的时候通知主对象

load逻辑修改：
    数据不存在的时候，调用自身的rebuild
"""

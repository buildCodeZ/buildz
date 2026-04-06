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
# log = logz.simple("recals.log")
class DoneRebuild(Exception):
    pass

pass
class ReCals(Base):
    def clean(self):
        self.base = 0
        self.total_size = 0
        self.recals = []
        # self.used = 0
        self.do_backward=False
    def init(self, max_size, rebuild = None, rng_dvs = [], max_remains=10, cuda_only = False):
        if type(max_size)==str:
            max_size = int(az.nsize(max_size))
        self.max_size = max_size
        self.max_remains = max_remains
        self.base = 0
        self.total_size = 0
        self.rebuild = rebuild
        self.rng_dvs = rng_dvs
        self.cuda_only = cuda_only
        # self.used = 0
        self.recals = []
        self.do_backward=False
    def inc_backward(self):
        self.do_backward=True
    # def inc_used(self):
    #     self.used+=1
    #     if self.used>=len(self.recals):
    #         self.clean()
    def call(self, fc, *a, **b):
        return self.forward(self.rng_dvs, fc, *a, **b)
    def analyze(self, fc, *a, **b):
        return self.analyzes(fc, *a, **b)[:2]
    def analyzes(self, fc, *a, **b):
        '''
            计算总缓存和单元最大缓存，不实际存储
        '''
        cache_sizes=[0,0,0]
        def save(tuple_data):
            u_size = dv.sizes(tuple_data)
            if u_size>cache_sizes[1]:
                cache_sizes[1]=u_size
            cache_sizes[0]+=u_size
            cache_sizes[2]+=1
            return -1
        def load(obj):
            raise "not impl"
        with torch.autograd.graph.saved_tensors_hooks(save, load):
            out = fc(*a, **b)
        return cache_sizes
    def forward(self,  rng_dvs, fc, *a, **b):
        if self.do_backward:
            self.clean()
        # log.info(f"do forward")
        recal = ReCal(self, self.rebuild, rng_dvs, self.cuda_only, self.max_remains)
        self.recals.append(recal)
        return recal.forward(fc, *a, *b)
    def add_size(self, size):
        self.total_size+=size
    def check_and_free(self, size, recal=None):
        assert size <= self.max_size, "uncalable case single size is bigger than max_size"
        if self.total_size+size<self.max_size:
            return
        free_size = self.total_size+size-self.max_size
        if recal is not None:
            free_size = recal.free_size(free_size)
            assert free_size<=0, f"unknown reason that caches can't free a: {free_size}"
            return
        for i in range(self.base, len(self.recals)):
            recal = self.recals[i]
            if recal.total_size>0:
                free_size = recal.free_size(free_size)
                if free_size<=0:
                    if recal.total_size==0:
                        i+=1
                    break
        self.base = i
        assert free_size<=0, f"unknown reason that caches can't free b: {free_size}"
    def cache_size(self, fmt=False):
        size = sum([recal.cache_size() for recal in reacals])
        if fmt:
            size = az.fmt_sz(size)
        return size

class ReCal(Base):
    '''
    '''
    def bind_rebuild(self, rebuild):
        self.rebuild = rebuild
    def bind_rng_dvs(self, rng_dvs):
        self.rng_dvs = rng_dvs
    def init(self, recals, rebuild = None, rng_dvs = [], cuda_only = False, max_remains = 10):
        self.recals = recals
        self.max_remains = max_remains
        self.caches = {}
        self.total_size = 0
        self.rebuild = rebuild
        self.abs = -1
        '0: normal, 1: wait_rebuild, 2: done_rebuild'
        self.status = 0 
        self.index=0 
        self.max_used = 0
        self.base=0
        self.save_count=0
        self.used = set()
        self.cuda_only = cuda_only
        if type(rng_dvs) == int:
            rng_dvs = [rng_dvs]
        self.rng_dvs = rng_dvs
        self.rng_states = []
        self.bak_rng_states = []
        self.cuda_autocasts=None
        self.cpu_autocasts=None
    def get_rngs(self, rng_states = None):
        if self.rng_dvs is None:
            return
        if rng_states is None:
            rng_states = self.rng_states
        for i in self.rng_dvs:
            if i == 'cpu' or i == -1:
                rng_states.append(torch.get_rng_state())
                continue
            with torch.cuda.device(i):
                rng_states.append(torch.cuda.get_rng_state())
    def set_rngs(self, rng_states = None):
        if self.rng_dvs is None:
            return
        if rng_states is None:
            rng_states = self.rng_states
        for i, st in zip(self.rng_dvs, rng_states):
            if i =='cpu' or i == -1:
                torch.set_rng_state(st)
                continue
            with torch.cuda.device(i):
                torch.cuda.set_rng_state(st)
    def forward_init(self, status=0):
        if status == 0:
            self.used = set()
            self.caches = {}
            self.rng_states = []
            self.bak_rng_states = []
            self.get_rngs()
            self.abs=-1
            self.save_count = 0
            self.total_size = 0
            self.max_used = 0
            self.cuda_autocasts={"enabled": torch.is_autocast_enabled(),
                           "dtype": torch.get_autocast_gpu_dtype(),
                           "cache_enabled": torch.is_autocast_cache_enabled()}
            self.cpu_autocasts={"enabled": torch.is_autocast_cpu_enabled(),
                           "dtype": torch.get_autocast_cpu_dtype(),
                           "cache_enabled": torch.is_autocast_cache_enabled()}
        else:
            self.set_rngs()
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
        auto_cuda = None
        auto_cpu = None
        if status!= 0:
            if self.cuda_autocasts and self.cuda_autocasts["enabled"]:
                auto_cuda = torch.cuda.amp.autocast(**self.cuda_autocasts)
            if self.cpu_autocasts and self.cpu_autocasts["enabled"]:
                auto_cpu = torch.cuda.amp.autocast(**self.cpu_autocasts)
        def wrap_enter():
            self.forward_init(status)
            if auto_cuda:
                auto_cuda.__enter__()
            if auto_cpu:
                auto_cpu.__enter__()
            obj.__enter__()
        def wrap_out(exc_type, exc_val, exc_tb):
            obj.__exit__(exc_type, exc_val, exc_tb)
            if auto_cpu:
                auto_cpu.__exit__(exc_type, exc_val, exc_tb)
            if auto_cuda:
                auto_cuda.__exit__(exc_type, exc_val, exc_tb)
        return pyz.With(wrap_enter, wrap_out, True)
    def free_size(self, size):
        cut_size = 0
        cnt=0
        while size>cut_size and len(self.caches)>0:
            if self.base==self.abs and self.status!=0:
                break
            _, pop_size = self.caches.pop(self.base)
            # log.info(f"free {self.base}")
            cut_size+=pop_size
            self.base+=1
            cnt+=1
        assert cut_size>0, f"error in free_size({size}), not space can be free"
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
        # log.info(f"save {self.index}")
        self.max_used = max(self.max_used, self.index)
        self.index+=1
        if self.status==0:
            self.save_count+=1
        return self.index-1
    def do_rebuild(self):
        assert self.rebuild is not None, "use bind_rebuild(fc) to set a rebuild function"
        if self.rng_dvs and len(self.bak_rng_states)==0:
            self.get_rngs(self.bak_rng_states)
        with self._with_forward(1):
            with torch.enable_grad():
                try:
                    self.rebuild()
                except DoneRebuild as exp:
                    # log.info("done rebuild")
                    pass
        self.set_rngs(self.bak_rng_states)
    def tensor_load(self, key):
        self.recals.inc_backward()
        if type(key)!=int:
            return key
        obj, size = self.caches.pop(key, (None, 0))
        if obj is None:
            self.abs = key
            self.do_rebuild()
            obj, size = self.caches.pop(key)
        # log.info(f"load {key}")
        self.total_size-=size
        self.recals.add_size(-size)
        self.used.add(key)
        if key == self.max_used:
            self.max_used-=1
        while self.max_used-key>self.max_remains:
            if self.max_used in self.caches:
                _, _size = self.caches.pop(self.max_used)
                self.total_size-=_size
                self.recals.add_size(-_size)
            self.max_used-=1
        return obj
    def cache_size(self, fmt=False):
        size = self.total_size
        if fmt:
            size = az.fmt_sz(size)
        return size

def recals_with_rngs(max_size:int, rng_devices:list|str|int|tuple|torch.Tensor="all",max_remains=10, rebuild = None, cuda_only=False):
    '''
        rng_devices: 
            需要在计算前存储随机数种子的显卡设备，避免在反向梯度计算时重新计算因为网络层运行的随机性导致和之前计算的不不一样（比如dropout）
            取值:
            str: 
                "null", "none": no cuda device
                "all", scan all cuda devices and cpu device
                "cuda", scan all cuda devices
                "cpu", cpu only
            int: torch.cuda.device(rng_devices)
            list: [torch.cuda.device(i) for i in rng_devices]
            torch.Tensor: [rng_devices.get_device()]
        max_remains:
            默认取值10，反向计算backward的时候，使用到第i个缓存的时候，将缓存索引为i+max_remains以上的缓存清空
            反向的时候是用一个缓存删一个缓存，并且是从后面存的缓存开始用，一直用到前面存的缓存
            但pytorch有个坑，在前向计算forward时候存的缓存在backward的时候不一定都会使用，可能有少量缓存直接不用了，这时候需要手动清理下，避免其占据设置的缓存上限却完全没用。
            测试发现backward的时候缓存使用基本都是一直往前使用，局部存在少量的乱序，比如存的缓存顺序是1，2，3，4，5，6，7，8，9，10，用的时候可能是10，9，7，8，4，6，5，3，2，1，乱序基本是单个网络层存多个缓存的时候，该网络层下的缓存使用可能是随机的，单个网络层基本就存0到4个缓存，max_remains使用默认值10基本足够了
    '''
    if isinstance(rng_devices, torch.Tensor):
        rng_devices = [rng_devices.get_device()]
    elif type(rng_devices)==str:
        assert rng_devices in {"null","none","all", 'cpu', 'cuda'},f"unknown rng_devices str: {rng_devices}, should be 'all' or 'null'"
        if rng_devices=="all":
            rng_devices = list(range(torch.cuda.device_count()))+[-1]
        if rng_devices=="cuda":
            rng_devices = list(range(torch.cuda.device_count()))
        elif rng_devices=="cpu":
            rng_devices = [-1]
        else:
            rng_devices = []
    elif type(rng_devices)==int:
        rng_devices = [rng_devices]
    assert type(rng_devices) in {tuple, list}, "rng_devices should be int or str or list or tuple"
    return ReCals(max_size, rebuild, rng_devices, max_remains, cuda_only)



"""#

集合的形式

recals()调用的时候生成一个子对象，
save逻辑修改：
    空间不够的时候，调用主对象的清理指令，或者干脆由主对象判断，主对象判断空间不够按顺序调用子对象的释放函数，直到空间足够，子对象会在自身空间为0或非0的时候通知主对象

load逻辑修改：
    数据不存在的时候，调用自身的rebuild
"""

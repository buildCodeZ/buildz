'''

测试用，别用
'''

from . import dv
from .. import az
import torch
from torch import nn
from buildz import log as logz
from buildz.base import Base
from buildz import pyz, dz

# log = logz.simple("recal.log")("recal")
class DoneRebuild(Exception):
    pass

pass
class ReCal(Base):
    '''
    '''
    def bind_rebuild(self, rebuild):
        self.rebuild = rebuild
    def bind_rng_dvs(self, rng_dvs):
        self.rng_dvs = rng_dvs
    def init(self, max_size, rebuild = None, rng_dvs = [],cuda_only=False):
        if type(max_size)==str:
            max_size = int(az.nsize(max_size))
        self.caches = {}
        self.total_size = 0
        self.max_size = max_size
        self.rebuild = rebuild
        self.abs = -1
        '0: normal, 1: wait_rebuild, 2: done_rebuild'
        self.status = 0 
        self.index=0 
        self.base=0
        self.cuda_only = cuda_only
        self.used = set()
        if type(rng_dvs) in {bool, int}:
            if rng_dvs:
                rng_dvs = [0]
        self.rng_dvs = rng_dvs
        self.rng_states = []
    def get_rngs(self):
        if self.rng_dvs is None:
            return
        for i in self.rng_dvs:
            with torch.cuda.device(i):
                self.rng_states.append(torch.cuda.get_rng_state())
    def set_rngs(self):
        if self.rng_dvs is None:
            return
        for i, st in zip(self.rng_dvs, self.rng_states):
            with torch.cuda.device(i):
                torch.cuda.set_rng_state(st)
    def forward_init(self, status=0):
        if status == 0:
            self.used = set()
            self.caches = {}
            self.rng_states = []
            self.get_rngs()
        else:
            self.set_rngs()
        self.total_size = 0
        self.status = status
        self.index=0 
        self.base=0 
    def call(self, fc, *a, **b):
        return self.forward(fc, *a, **b)
    def forward(self, fc, *a, **b):
        # log.info(f"do forward")
        return self.wrap_forward(lambda :fc(*a, **b))
    def wrap_forward(self, fc):
        self.rebuild = fc or self.rebuild
        with self._with_forward(0):
            return self.rebuild()
        # return self._wrap_forward(rebuild, 0)
    def _with_forward(self, status=0):
        obj = torch.autograd.graph.saved_tensors_hooks(self.tensor_save, self.tensor_load)
        def wrap_enter():
            self.forward_init(status)
            obj.__enter__()
        def wrap_out(exc_type, exc_val, exc_tb):
            obj.__exit__(exc_type, exc_val, exc_tb)
        return pyz.With(wrap_enter, wrap_out, True)
    def tensor_save(self, tuple_data):
        size, is_cuda = dv.sizes_cuda(tuple_data)
        if not is_cuda and self.cuda_only:
            return tuple_data
        assert size <= self.max_size, "uncalable case single size is bigger than max_size"
        if self.status==2 and self.index in self.used:
            raise DoneRebuild()
        while self.total_size+size>self.max_size:
            _, pop_size = self.caches.pop(self.base)
            # log.info(f"free {self.base}")
            self.total_size-=pop_size
            self.base+=1
        self.caches[self.index] = (tuple_data, size)
        # log.info(f"save {self.index}")
        self.total_size+=size
        if self.index==self.abs:
            self.status = 2
        self.index+=1
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
        obj, _ = self.caches.pop(key, (None, None))
        if obj is None:
            self.abs = key
            self.do_rebuild()
            obj = self.caches.pop(key)[0]
        # log.info(f"load {key}")
        self.used.add(key)
        return obj
    def cache_size(self, fmt=False):
        size = self.total_size
        if fmt:
            size = az.fmt_sz(size)
        return size

def recal_with_rngs(max_size:int, rng_devices:list|str|int|tuple|torch.Tensor="all",rebuild = None, cuda_only = False):
    '''
        rng_devices: 
            需要在计算前存储随机数种子的显卡设备，避免在反向梯度计算时重新计算因为网络层运行的随机性导致和之前计算的不不一样（比如dropout）
            取值:
            str: 
                "null", "none": no cuda device
                "all", scan all cuda devices
            int: torch.cuda.device(rng_devices)
            list: [torch.cuda.device(i) for i in rng_devices]
            torch.Tensor: [rng_devices.get_device()]
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
    return ReCal(max_size, rebuild, rng_devices, cuda_only)

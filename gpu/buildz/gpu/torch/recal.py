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

# 测试代码目前先注释掉，可能还要测试，后面确定测试完全后会删掉
# log = logz.simple("test_torch.log", shows=[])
# log = log("recal.hook")
#log.info("new test start")
class DoneRebuild(Exception):
    pass

pass
# def fmt(datas):
#     if type(datas)==tuple:
#         rst = [fmt(k) for k in datas]
#         rs = ", ".join(rst)
#         rs = f"tp({rs})"
#         return rs
#     if datas is None:
#         return ""
#     return str(datas.size())
class ReCal(Base):
    '''
        设置一个
        和“梯度检查点（Gradient Checkpointing）”相似的原理，不同的地方：
            用起来更简单，配置更简单，相对的
    '''
    def bind_rebuild(self, rebuild):
        self.rebuild = rebuild
    def bind_rng_dvs(self, rng_dvs):
        self.rng_dvs = rng_dvs
    def debug_ns(self, net):
        return "net"
    def init(self, max_size, debug_ns=None, rebuild = None, rng_dvs = []):
        if type(max_size)==str:
            max_size = int(az.nsize(max_size))
        # print(f"max_size: {max_size}, {az.fmt_sz(max_size)}")
        self.caches = {}
        self.total_size = 0
        self.max_size = max_size
        self.debug_ns = debug_ns or self.debug_ns
        self.rebuild = rebuild
        self.abs = -1
        '0: normal, 1: wait_rebuild, 2: done_rebuild'
        self.status = 0 
        self.index=0 
        self.base=0
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
    def forward_after(self, model, ins, outs):
        #log.info(f"self.forward_after for {self.debug_ns(model), fmt(ins), fmt(outs)}")
        if self.status == 2:
            raise DoneRebuild()
    def forward_before(self, model, ins):
        #log.info(f"self.forward_before for {self.debug_ns(model), fmt(ins)}")
        return ins
    def backward_after(self, model, grad_up, grad_src):
        #log.info(f"self.backward_after for {self.debug_ns(model), fmt(grad_up), fmt(grad_src)}")
        return grad_up
    def tensor_save(self, tuple_data):
        #log.info(f"call tensor_save for {self.index}")
        size, is_cuda = dv.sizes_cuda(tuple_data)
        if not is_cuda:
            return tuple_data
        assert size <= self.max_size, "uncalable case single size is bigger than max_size"
        if self.status==2 and self.index in self.used:
            #log.info(f"stop tensor_save at {self.index}")
            raise DoneRebuild()
        while self.total_size+size>self.max_size:
            #log.info(f"del {self.base} for caches reach max: {self.total_size+size}/{self.max_size}")
            _, pop_size = self.caches.pop(self.base)
            self.total_size-=pop_size
            self.base+=1
        self.caches[self.index] = (tuple_data, size)
        self.total_size+=size
        if self.index==self.abs:
            self.status = 2
            #log.info(f"abs {self.abs} is reget")
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
        #log.info(f"call tensor_load for {key}")
        obj, _ = self.caches.pop(key, (None, None))
        if obj is None:
            #log.info(f"abs {key}, do rebuild"))
            self.abs = key
            self.do_rebuild()
            #log.info(f"reget {key}, done rebuild")
            obj = self.caches.pop(key)[0]
        self.used.add(key)
        return obj
    def cache_size(self, fmt=False):
        size = self.total_size
        if fmt:
            size = az.fmt_sz(size)
        return size

def recal_with_rngs(max_size:int, rng_devices:list|str|int|tuple="all",rebuild = None):
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
    if type(rng_devices)==str:
        assert rng_devices in {"null","none","all"},f"unknown rng_devices str: {rng_devices}, should be 'all' or 'null'"
        if rng_devices=="all":
            rng_devices = list(range(torch.cuda.device_count()))
        else:
            rng_devices = []
    elif type(rng_devices)==int:
        rng_devices = [rng_devices]
    assert type(rng_devices) in {tuple, list}, "rng_devices should be int or str or list or tuple"
    print(f"rng_devices: {rng_devices}")
    return ReCal(max_size, None, rebuild, rng_devices)

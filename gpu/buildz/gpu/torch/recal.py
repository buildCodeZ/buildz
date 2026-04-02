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
# log = logz.simple("test_torch.log", shows=[])
# log = log("recal.hook")
#log.info("new test start")
class DoneRebuild(Exception):
    pass

pass
def fmt(datas):
    if type(datas)==tuple:
        rst = [fmt(k) for k in datas]
        rs = ", ".join(rst)
        rs = f"tp({rs})"
        return rs
    if datas is None:
        return ""
    return str(datas.size())
class ReCal(Base):
    def bind_rebuild(self, rebuild):
        self.rebuild = rebuild
    def debug_ns(self, net):
        return "net"
    def init(self, max_size, debug_ns=None, rebuild = None):
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
    def forward_init(self, status=0):
        if status == 0:
            self.used = set()
            self.caches = {}
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
        size = dv.sizes(tuple_data)
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
        #log.info(f"call tensor_load for {key}")
        obj, _ = self.caches.pop(key, (None, None))
        if obj is None:
            #log.info(f"abs {key}, do rebuild")
            self.abs = key
            self.do_rebuild()
            #log.info(f"reget {key}, done rebuild")
            obj = self.caches.pop(key)[0]
        self.used.add(key)
        return obj
'''
python -m buildz.gpu.test.demo
'''

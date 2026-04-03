'''

测试模型的钩子函数调用时间
'''

import torch
from torch import nn
from buildz import log as logz
from buildz.base import Base
from buildz import pyz, dz
log = logz.simple("test_torch.log")
log = log("test.torch.hook")
log.info("new test start")
def fmt(datas):
    if type(datas)==tuple:
        rst = [fmt(k) for k in datas]
        rs = ", ".join(rst)
        rs = f"tp({rs})"
        return rs
    if datas is None:
        return ""
    return str(datas.size())
class Hooks(Base):
    def bind(self, net):
        key = id(net)
        dz.init(self.hooks, key, [])
        self.ns[key] = f"net{len(self.ns)}"
        hooks = []
        hooks += [net.register_forward_pre_hook(self.forward_before)]
        hooks+=[net.register_forward_hook(self.forward_after)]
        if hasattr(nets[0], "register_full_backward_hook"):
            hooks+=[net.register_full_backward_hook(self.backward_after)]
        else:
            hooks+=[net.register_backward_hook(self.backward_after)]
        self.hooks[key]+=hooks
    def unbind(self, net):
        key = id(net)
        if key not in self.hooks:
            return
        hooks = self.hooks.pop(key)
        for hook in hooks:
            hook.remove()
    def binds(self, nets):
        for net in nets:
            self.bind(net)
    def unbinds(self, nets = None):
        if nets:
            for net in nets:
                self.unbind(net)
                return
        for hooks in self.hooks.values():
            for hook in hooks:
                hook.remove()
        self.hookds = {}
    def bind_rebuild(self, rebuild):
        self.rebuild = rebuild
    def ni(self, model):
        key = id(model)
        return self.ns[key]
    def init(self, nets=None):
        self.hooks = {}
        self.ns = {}
        self.caches = []
        if nets:
            self.binds(nets)
    def forward_done(self):
        log.info(f"self.forward_done")
    def forward_init(self):
        log.info(f"self.forward_init")
        self.caches = []
    def wrap_forward(self):
        obj = torch.autograd.graph.saved_tensors_hooks(self.tensor_save, self.tensor_load)
        def wrap_enter():
            self.forward_init()
            obj.__enter__()
        def wrap_out(exc_type, exc_val, exc_tb):
            obj.__exit__(exc_type, exc_val, exc_tb)
            self.forward_done()
        return pyz.With(wrap_enter, wrap_out, True)
    def forward_after(self, model, ins, outs):
        log.info(f"self.forward_after for {self.ni(model), fmt(ins), fmt(outs)}")
    def forward_before(self, model, ins):
        log.info(f"self.forward_before for {self.ni(model), fmt(ins)}")
        return ins
    def backward_after(self, model, grad_up, grad_src):
        log.info(f"self.backward_after for {self.ni(model), fmt(grad_up), fmt(grad_src)}")
        return grad_up
    def tensor_save(self, tuple_data):
        log.info(f"call tensor_save for {len(self.caches)}")
        self.caches.append(tuple_data)
        return len(self.caches)-1
    def tensor_load(self, key):
        log.info(f"call tensor_load for {key}")
        obj = self.caches[key]
        self.caches[key] = None
        return obj
    def backward_init(self):
        log.info(f"self.backward_init")
    def backward_done(self):
        log.info(f"self.backward_done")
    def wrap_backward(self):
        def wrap_enter():
            self.backward_init()
        def wrap_out(exc_type, exc_val, exc_tb):
            self.backward_done()
        return pyz.With(wrap_enter, wrap_out, True)
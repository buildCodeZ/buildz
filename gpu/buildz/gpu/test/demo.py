'''

测试模型的钩子函数调用时间
'''

from . import dv
import torch
from torch import nn
from buildz import log as logz
from buildz.base import Base
from buildz import pyz, dz
log = logz.simple("test_torch.log")
log = log("test.torch.hook")
log.info("new test start")
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
class Hooks(Base):
    def bind(self, net):
        key = id(net)
        dz.init(self.hooks, key, [])
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
    def init(self, nets=None, rebuild=None, max=10240):
        self.hooks = {}
        self.caches = {}
        self.max = max
        self.rebuild = rebuild
        self.abs = -1
        '0: normal, 1: wait_rebuild, 2: done_rebuild'
        self.status = 0 
        self.index=0 
        self.base=0 
        if nets:
            self.binds(nets)
    def forward_init(self, status=0):
        self.status = status
        self.index=0 
        self.base=0 
    def wrap_forward(self, status=0):
        obj = torch.autograd.graph.saved_tensors_hooks(self.tensor_save, self.tensor_load)
        def wrap_enter():
            self.forward_init(status)
            obj.__enter__()
        def wrap_out(exc_type, exc_val, exc_tb):
            obj.__exit__(exc_type, exc_val, exc_tb)
            #self.wrap_forward_after()
        return pyz.With(wrap_enter, wrap_out, True)
    def forward_after(self, model, ins, outs):
        log.info(f"self.forward_after for {ni(model), fmt(ins), fmt(outs)}")
        if self.status == 2:
            raise DoneRebuild()
    def forward_before(self, model, ins):
        log.info(f"self.forward_before for {ni(model), fmt(ins)}")
        return ins
    def backward_after(self, model, grad_up, grad_src):
        log.info(f"self.backward_after for {ni(model), fmt(grad_up), fmt(grad_src)}")
        return grad_up
    def tensor_save(self, tuple_data):
        log.info(f"call tensor_save for {len(self.caches)}")
        if self.status==2 and self.index in self.caches:
            raise DoneRebuild()
        while len(self.caches)>self.max:
            log.info(f"del {self.base} for caches reach max: {len(self.caches)}/{self.max}")
            del self.caches[self.base]
            self.base+=1
        self.caches[self.index] = tuple_data
        if self.index==self.abs:
            self.status = 2
        self.index+=1
        return self.index-1
    def do_rebuild(self):
        assert self.rebuild is not None, "use bind_rebuild(fc) to set a rebuild function"
        with self.wrap_forward(1):
            with torch.enable_grad():
                try:
                    self.rebuild()
                except DoneRebuild as exp:
                    pass
    def tensor_load(self, key):
        log.info(f"call tensor_load for {key}")
        obj = self.caches.pop(key, None)
        if obj is None:
            log.info(f"abs {key}, do rebuild")
            self.abs = key
            self.do_rebuild()
            obj = self.caches.pop(key)
        return obj
    def wrap_backward(self):
        def wrap_enter():
            self.wait_backup_models = []
            self.before_backward()
        def wrap_out(exc_type, exc_val, exc_tb):
            for model in self.wait_backup_models:
                self.hook_backward_after(model)
            self.after_backward()
        return pyz.With(wrap_enter, wrap_out, True)
hooks = Hooks(max=20)
nets0 = [nn.Linear(3,4), nn.Linear(4,3), nn.Linear(3,3)]
nets1 = [nn.Linear(3,4), nn.Linear(4,3), nn.Linear(3,3)]
nets2 = [nn.Linear(3,4), nn.Linear(4,3), nn.Linear(3,3)]

nets0 = nn.Sequential(*nets0)
nets1 = nn.Sequential(*nets1)
nets2 = nn.Sequential(*nets2)
ns = {}
ns[id(nets0)] = "nets0"
ns[id(nets1)] = "nets1"
ns[id(nets2)] = "nets2"
ni = lambda n:ns[id(n)]
nets = [nets0, nets1, nets0, nets2, nets0]
hk_nets = [nets0, nets1, nets2]
model = nn.Sequential(*nets)
batch=2
data = torch.randn(batch, 3)

[hooks.bind(net) for net in hk_nets]
hooks.bind_build(lambda :model(data))
log.info(f"FORWARD\n\n")
with hooks.wrap_forward():
    out = model(data)

log.info(f"BACKWARD\n\n")
loss = out.mean()
log.info(f"loss: {loss}, {type(loss)}")
loss.backward()

'''
python -m buildz.gpu.test.demo
'''

#
import torch
from torch import nn
import threading as th
from ... import Base
import numpy as np
class DictCache(Base):
    '''
        用处：显存不够的时候，可以用本代码框架，代码会在forward和backward的时候自动把nets列表里需要计算的模型放入显存，不需要计算的放到内存，需要进行卷积训练的时候用处比较大（卷积计算显卡比CPU强太多）
        使用本框架需要传入手动拆分成多个小模型的模型列表nets
        测试大概有纯显卡二分之一到三分之一的性能，起码比cpu好，尤其是进行卷积计算，比cpu好太多
        DictCache里的Dict意思是传入的模型列表nets会存字典里，Cache就是用内存作为显存的缓存
        代码实现原理是利用pytorch的几个勾子函数：
            model.register_forward_pre_hook会在模型forward之前调用
            model.register_full_backward_hook会在模型反向梯度计算之后调用
            torch.autograd.graph.saved_tensors_hooks(hook_pack, hook_unpack):
                hook_pack会在模型forward的时候把之后反向梯度计算要用的tensor进行存储
                hook_unpack是在反向梯度计算的时候取回forward存储的tensor
        代码例子:
        
        from buildz.gpuz.torch import DictCache
        from torch import nn,optim
        model1 = nn.Sequential(*[nn.Linear(1024,1024) for i in range(10)])
        model2 = nn.Sequential(*[nn.Linear(1024,1024) for i in range(10)])
        model3 = nn.Sequential(*[nn.Linear(1024,1024) for i in range(10)])
        opt1 = optim.Adam(model1.parameters(), lr=0.001)
        opt2 = optim.Adam(model2.parameters(), lr=0.001)
        opt3 = optim.Adam(model3.parameters(), lr=0.001)
        models = [model1,model2,model3]
        opts = [opt1,opt2,opt3]
        real_model = nn.Sequential(*models)
        loss_fn = torch.nn.MSELoss()
        def opt_step(net, opt):
            # 如果模型只是用来测试，不做训练，可以不传该函数，同时opts传入空就可以
            # 对模型的一些其他优化，可以写可以不写，主要是调用opt.step()进行当前小模型的模型训练
            # torch.nn.utils.clip_grad_norm_(net.parameters(), max_norm=1.0)
            opt.step()
        cache = DictCache([torch.device('cuda'), torch.device('cpu')],models,opts,3,opt_step)

        # 训练:
        [md.train() for md in models]
        for inputs,targets in dataloader: #批量数据集，这个自己实现
            [opt.zero_grad() for opt in opts]
            outs = cmodel.do_forward(lambda:real_model(inputs))
            loss = loss_fn(outs, targets)
            cmodel.do_backward(lambda: loss.backward())
            # opt.step()在do_backward里会自动调用
            print(loss.item())

        # 测试:
        with torch.no_grad():
            outputs = cmodel.do_forward(inputs)
        print(outputs)
    '''
    def init(self, dvs, nets, opts=None, win_size=1, backward_deal=None):
        '''
            dvs[0]: 显卡设备，应该传入torch.device('cuda')
            dvs[1]: CPU设备，应该传入torch.device('cpu')
            dvs如果都传入torch.device('cpu')，则是完全CPU存储和计算
                如果都传入torch.device('cuda')，则是完全显卡存储和计算
            dvs[0]=dvs[1]的时候，可以不传列表，直接传一个dv就可以了
            nets: 小模型列表
            opts: 每个小模型对应的可选参数列表，如果要做训练，需要传入该项
            win_size: 显卡里最多存放多少个nets里的小模型，多线程的时候用处会比较大（后续开发），单线程的时候也是越大越好
            backward_deal: 梯度反向传播后的调用函数，训练的时候要传，本框架代码在第i个小模型梯度反向传播后会调用backward_deal(nets[i], opts[i])，里面加上梯度反向传播后需要做的代码，如果只是测试(eval)，不训练，该项可以不传
        '''
        if type(dvs) not in (list,tuple):
            dvs = [dvs]
        self.gdv = dvs[0]
        self.cdv = dvs[-1]
        [net.register_forward_pre_hook(self.hook_forward_pre) for net in nets]
        #[net.register_forward_hook(self.hook_forward) for net in nets]
        [net.register_full_backward_hook(self.hook_backward) for net in nets]
        self.src_nets = nets
        self.nets = {id(net):net for net in nets}
        self.ctxs = {id(net):[] for net in nets}
        if opts is not None:
            opts = {id(net): opt for net,opt in zip(nets, opts)}
        self.opts = opts
        self.pools = []
        self.win_size = win_size
        self.backward_deal = backward_deal
        self.nears = {id(net):[-1,-1] for net in nets}
        self.curr = -1
        self.done_backward = -1
    def ctxs_to(self, i, dv):
        if dv is None:
            self.ctxs[i] = []
        else:
            self.ctxs[i] = [k.to(dv) for k in self.ctxs[i]]
    def copy_backward(self, nid):
        for c_id in self.pools:
            self.nets[c_id].to(self.cdv)
            self.ctxs_to(c_id, None)
        self.pools = []
        self.nets[nid].to(self.gdv)
        self.ctxs_to(nid, self.gdv)
        self.pools.append(nid)
        next_id = nid
        for i in range(self.win_size-1):
            next_id = self.nears[next_id][1]
            if next_id<0:
                break
            self.nets[next_id].to(self.gdv)
            self.ctxs_to(next_id, self.gdv)
            self.pools.append(next_id)
    def copy_forward(self, nid, model):
        for c_id in self.pools:
            self.nets[c_id].to(self.cdv)
            self.ctxs_to(c_id, self.cdv)
        self.pools = []
        model.to(self.gdv)
        self.pools.append(nid)
        next_id = nid
        for i in range(self.win_size-1):
            next_id = self.nears[next_id][0]
            if next_id<0:
                break
            self.nets[next_id].to(self.gdv)
            self.pools.append(next_id)
    def hook_forward_pre(self, model, ins):
        nid = id(model)
        if nid not in self.pools:
            self.copy_forward(nid, model)
        if self.curr>=0:
            self.nears[self.curr][0] = nid
        self.curr = nid
    def do_forward(self, fc):
        self.ctxs = {k:[] for k in self.nets}
        with torch.autograd.graph.saved_tensors_hooks(self.hook_pack, self.hook_unpack):
            rst = fc()
        return rst
    def wrap_backward_deal(self, net_id):
        if self.backward_deal is None:
            return
        self.backward_deal(self.nets[net_id], self.opts[net_id])
    def hook_backward(self, model, grad_ins, grad_outs):
        nid = id(model)
        self.wrap_backward_deal(nid)
    def hook_pack(self, dt):
        # forward时候为了后面计算梯度存的缓存，放到列表里方便转cpu和gpu
        self.ctxs[self.curr].append(dt)
        return self.curr, len(self.ctxs[self.curr])-1
    def hook_unpack(self, x):
        nid = x[0]
        if nid not in self.pools:
            self.copy_backward(nid)
        dt = self.ctxs[nid][x[1]]
        if self.curr>=0:
            self.nears[self.curr][1] = nid
        self.curr = nid
        return dt
    def do_backward(self, fc):
        self.curr = -1
        fc()
        self.wrap_backward_deal(self.curr)

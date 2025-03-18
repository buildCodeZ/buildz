#


'''
测试用DictCache和不用DictCache的时候，反向梯度是否一样，代码比较杂，不建议看，测试结果是效果一致
'''
import sys
from buildz.gpuz.torch import DictCache
import torch,time
from torch import nn,optim
from torch.utils.data import DataLoader, Dataset
cpu = torch.device('cpu')
cuda = cpu
if torch.cuda.is_available():
    cuda = torch.device('cuda')
def sz(tensor):
    return tensor.element_size()*tensor.nelement()
class ConvModel(nn.Module):
    def __init__(self, dims, num, ins_channels, middle_channels):
        super().__init__()
        nets=[]
        for i in range(num):
            nets.append(nn.Conv2d(ins_channels, middle_channels, 5, padding=2))
            nets.append(nn.Conv2d(middle_channels, ins_channels, 5, padding=2))
            nets.append(nn.LeakyReLU())
        self.nets = nn.Sequential(*nets)
    def dv(self):
        return self.nets[0].bias.device
    def forward(self, inputs):
        return self.nets(inputs)
    def size(self):
        total = 0.0
        for net in self.nets:
            if not hasattr(net, "weight"):
                continue
            w = net.weight
            b = net.bias
            total+=sz(w)+sz(b)
        return total

pass
class ResNet(nn.Module):
    def __init__(self, net):
        super().__init__()
        self.net = net
    def forward(self, inputs):
        return inputs+self.net(inputs)
class TestDataset(Dataset):
    def __init__(self, n, dims, channels):
        self.n = n
        self.dims = dims
        self.datas = torch.rand(n, channels, dims,dims)
        print(f"data size: {sz(self.datas)/1024/1024/1024} GB")
    def __len__(self):
        return self.n
    def __getitem__(self, i):
        return self.datas[i]
        return torch.rand(self.dims)

pass
def gen(dims, nets_num, channels, middle_channels, num_conv, lr):
    mds = []
    base = None
    for i in range(num_conv):
        nets = [ConvModel(dims, nets_num, channels, middle_channels) for i in range(2)]
        mds+=nets
        if base is not None:
            nets = [nets[0], base, nets[1]]
        nets = nn.Sequential(*nets)
        base = ResNet(nets)
    fullnet = base
    opts =[optim.Adam(md.parameters(), lr=lr) for md in mds]
    gopt = optim.Adam(fullnet.parameters(), lr=lr)
    return mds, fullnet, opts, gopt
def do_save(mds, gmodel, opts, gopt, fp):
    save = SaveModel(gmodel=gmodel, gopt=gopt)
    save.set_list("md", mds)
    save.set_list("opt", opts)
    save.save(fp)
def do_load(mds, gmodel, opts, gopt, fp):
    save = SaveModel(gmodel=gmodel, gopt=gopt)
    save.set_list("md", mds)
    save.set_list("opt", opts)
    save.load(fp)
    mds = save.get_list("md")
    opts = save.get_list("opt")
    gmodel = save.gmodel
    gopt = save.gopt
    return mds, gmodel, opts, gopt

pass
    


from pyz.nn.dv import SaveModel
def fc_opt(net, opt):
    torch.nn.utils.clip_grad_norm_(net.parameters(), max_norm=1.0)
    opt.step()
def test():
    nets=2
    channels=10
    middle_channels = 30
    dims=64
    trains = 5
    datas = 6
    batch=2
    lr=0.0001
    win_size=3
    num_conv = 6
    num_ln = 3
    mds, gmodel, opts, gopt = gen(dims, nets, channels, middle_channels, num_conv, lr)
    fp = "tmp.dt"
    print(mds[0].nets[0].weight.mean(), mds[0].nets[0].bias.grad)
    #do_save(mds, gmodel, opts, gopt, fp)
    mds, gmodel, opts, gopt = do_load(mds, gmodel, opts, gopt, fp)
    print(mds[0].nets[0].weight.mean(), mds[0].nets[0].bias.grad)
    mds_sz = [md.size() for md in mds]
    print(f"Model Size: {sum(mds_sz)/1024/1024/1024} GB")
    #cuda=cpu
    ds = TestDataset(datas, dims, channels)
    dl = DataLoader(ds, batch)
    #return
    loss_fn = torch.nn.MSELoss()
    dt = list(dl)[0].to(cuda)
    dt[:] = 0.1
    print("start train")
    gmodel = gmodel.to(cuda)
    gmodel.train()
    i_mds = 3
    i_nets = 1
    #
    for i in range(3):
        out = gmodel(dt)
        loss = loss_fn(out, dt)
        print(f"loss: {loss, type(loss)}")
        loss.backward()
        print("grad:",mds[i_mds].nets[i_nets].weight.mean(), mds[i_mds].nets[i_nets].bias.grad)
        gopt.zero_grad()
        mds, gmodel, opts, gopt = do_load(mds, gmodel, opts, gopt, fp)
        print("grad empty:", mds[i_mds].nets[i_nets].weight.mean(), mds[i_mds].nets[i_nets].bias.grad)
    #return
    gmodel.cpu()
    torch.cuda.empty_cache()
    dt[:]=0.9
    input("start middle:")
    md = DictCache([cuda, cpu], mds, opts, win_size, fc_opt)
    [k.train() for k in mds]
    [opt.zero_grad() for opt in opts]
    for i in range(3):
        out = md.do_forward(lambda :gmodel(dt))
        loss = loss_fn(out, dt)
        print(f"loss: {loss, type(loss)}")
        md.do_backward(lambda : loss.backward())
        print("grad:",mds[i_mds].nets[i_nets].weight.mean(), mds[i_mds].nets[i_nets].bias.grad)
        [opt.zero_grad() for opt in opts]
        mds, gmodel, opts, gopt = do_load(mds, gmodel, opts, gopt, fp)
        print("grad empty:", mds[i_mds].nets[i_nets].weight.mean(), mds[i_mds].nets[i_nets].bias.grad)
    return
    seq = nn.Sequential(*mds)
    [k.train() for k in mds]
    #with torch.no_grad():
    for i in range(trains):
        total_loss = 0
        curr=time.time()
        for dt in dl:
            dt=dt.to(cuda)
            [opt.zero_grad() for opt in opts] #这一步不必也扔gpu里计算吧，直接这样写了
            out = md.do_forward(lambda :seq(dt))
            loss = loss_fn(out, dt)
            print(f"loss: {loss, type(loss)}")
            md.do_backward(lambda : loss.backward())
            total_loss+=loss.item()
        sec = time.time()-curr
        print("train:", i, "loss:", total_loss/len(dl), "time:", sec)

    

pass
test()
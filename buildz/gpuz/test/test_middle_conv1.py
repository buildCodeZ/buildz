#

import sys
from buildz.gpuz.torch import CacheModel
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
        print(f"nets:{len(nets)}")
        self.nets = nn.Sequential(*nets)
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
def fc_opt(net, opt):
    torch.nn.utils.clip_grad_norm_(net.parameters(), max_norm=1.0)
    opt.step()
def test():
    nets=2
    channels=30
    middle_channels = 60
    dims=512
    trains = 5
    datas = 6
    batch=2
    lr=0.0001
    win_size=3
    num_conv = 11
    num_ln = 3
    mds = [ConvModel(dims, nets, channels, middle_channels) for i in range(num_conv)]
    mds_sz = [md.size() for md in mds]
    print(f"Model Size: {sum(mds_sz)/1024/1024/1024} GB")
    opts =[optim.Adam(md.parameters(), lr=lr) for md in mds]
    #cuda=cpu
    ds = TestDataset(datas, dims, channels)
    dl = DataLoader(ds, batch)
    #return
    loss_fn = torch.nn.MSELoss()
    print("start train")
    # nets= []
    # for md in mds:
    #     nets+=md.nets
    # gmodel = nn.Sequential(*nets)
    # gmodel = gmodel.to(cuda)
    # gopt = optim.Adam(gmodel.parameters(), lr=lr)
    # gmodel.train()
    # #with torch.no_grad():
    # for i in range(trains):
    #     total_loss = 0
    #     curr=time.time()
    #     for dt in dl:
    #         dt=dt.to(cuda)
    #         gopt.zero_grad()
    #         out = gmodel(dt)
    #         loss = loss_fn(out, dt)
    #         print(f"loss: {loss, type(loss)}")
    #         loss.backward()
    #         gopt.step()
    #         total_loss+=loss.item()
    #     sec = time.time()-curr
    #     print("train:", i, "loss:", total_loss/len(dl), "time:", sec)
    # del gmodel,gopt
    # torch.cuda.empty_cache()
    # input("start middle:")
    md = CacheModel(cuda, cpu, mds, opts, win_size, fc_opt)
    md.nfc("train")
    #with torch.no_grad():
    for i in range(trains):
        total_loss = 0
        curr=time.time()
        for dt in dl:
            dt=dt.to(cuda)
            [opt.zero_grad() for opt in opts] #这一步不必也扔gpu里计算吧，直接这样写了
            out = md.do_forward(dt)
            loss = loss_fn(out, dt)
            print(f"loss: {loss, type(loss)}")
            md.do_backward(lambda : loss.backward())
            total_loss+=loss.item()
        sec = time.time()-curr
        print("train:", i, "loss:", total_loss/len(dl), "time:", sec)

    

pass
test()


from buildz.gpuz.torch import DictCache
import torch, time
from torch import nn,optim
from torch.utils.data import DataLoader, Dataset
class TestDataset(Dataset):
    def __init__(self, num, dims, dtype=torch.float32):
        self.num = num
        self.dims = dims
        self.datas = torch.rand(num, dims).to(dtype)
        self.targets = torch.rand(num, dims).to(dtype)
        print(f"dataset:", self.datas.size(), self.datas.dtype)
    def __len__(self):
        return self.num
    def __getitem__(self, i):
        return self.datas[i], self.targets[i]
def datas(num, dims, batch_unit_size=10, dtype=torch.float32):
    dataset = TestDataset(num, dims, dtype)
    dataloader = DataLoader(dataset, batch_unit_size)
    return dataloader
def model(num_nets, dims, dtype=torch.float32):
    nets = [nn.Linear(dims,dims) for i in range(num_nets)]
    nets = nn.Sequential(*nets)
    nets=nets.to(dtype)
    return nets

loss_fn = torch.nn.MSELoss()
def train(data, md, num=10):
    md = md.cuda()
    dt, tdt = data
    dt = dt.cuda()
    tdt = tdt.cuda()
    opt = optim.Adam(md.parameters(), lr=0.001)
    md.train()
    curr=time.time()
    _loss=0
    for i in range(num):
        opt.zero_grad()
        out = md(dt)
        loss = loss_fn(out, tdt)
        loss.backward()
        _loss+=loss.cpu().item()
        opt.step()
    print(f"_loss: {_loss/num}")
    return (time.time()-curr)/num

def io(data, md, num=10):
    dt, tdt = data
    md.eval()
    curr=time.time()
    for i in range(num):
        dt=dt.cuda()
        # tdt=tdt.cuda()
        dt=dt.cpu()
        # tdt=tdt.cpu()
    return (time.time()-curr)/num

def eval(data, md, num=10):
    dt, tdt = data
    print(f"dt: {dt.size()}")
    print(f"md: {len(md)}")
    # exit(0)
    dt = dt.cuda()
    md=md.cuda()
    tdt = tdt.cuda()
    md.eval()
    curr=time.time()
    with torch.no_grad():
        for i in range(num):
            dt=dt.cuda()
            out = md(dt).cpu()
            dt=out
    return (time.time()-curr)/num

class Cost:
    def __init__(self, num_dt, num_net, dims, dtype):
        self.dts = datas(num_dt, dims, num_dt, dtype)
        print(f"dts:", len(self.dts))
        self.dt = list(self.dts)[0]
        self.net = model(num_net, dims, dtype)
    def eval(self, num=10):
        return eval(self.dt, self.net, num)
    def train(self, num=10):
        return train(self.dt, self.net, num)
    def io(self, num=10):
        return io(self.dt, self.net, num)

def build(num_dt, num_net, dims, dtype):
    return Cost(num_dt, num_net, dims, dtype)

def fmt(sz):
    units = "B,KB,MB,GB,TB".split(",")
    cnt=0
    while sz>1024:
        sz=sz/1024
        cnt+=1
    sz = "%.4f"%(sz,)
    s = f"{sz}{units[cnt]}"
    return s
def test():
    import sys
    args = sys.argv[1:]
    od = args.pop(0)[0].lower()
    num_dt = 10 if len(args)==0 else int(args.pop(0))
    num_net = 10 if len(args)==0 else int(args.pop(0))
    dims = 10 if len(args)==0 else int(args.pop(0))
    count = 10 if len(args)==0 else int(args.pop(0))
    dtypes = {}
    dtypes[16] = torch.float16
    dtypes[32] = torch.float32
    dtype = torch.float32 if len(args)==0 else dtypes[int(args.pop(0))]
    print(f"num_dt: {num_dt}, num_net: {num_net}, dims: {dims}, count: {count}, dtypes: {dtype}")
    count_dt = num_dt*dims
    count_net = num_net*dims*dims
    unit = 4 if dtype==torch.float32 else 2
    sz_dt = count_dt*unit
    sz_net = count_net*unit
    print(f"data size: {fmt(sz_dt)}, model size: {fmt(sz_net)}")
    cst = Cost(num_dt, num_net, dims, dtype)
    fcs = {}
    fcs['t'] = cst.train
    fcs['e'] = cst.eval
    fcs['i'] = cst.io
    print(f"start")
    sec = fcs[od](count)
    sec = "%.4f"%(sec,)
    print(f"data size: {fmt(sz_dt)}, model size: {fmt(sz_net)}")
    print(f"time cost: {sec} sec")

if __name__=="__main__":
    test()

pass


"""
python -m buildz.gpuz.test.cost i 4096 4096 1024 10 32

cst=Cost(4096, 4096, 1024, torch.float32)
"""
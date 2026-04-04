
from buildz.gpu.torch import recal, dv, recals
from buildz.gpu import az
import torch,time
from torch import nn, optim
from buildz import log as logz
from os.path import dirname, join, isfile
from torch.utils.checkpoint import checkpoint
curr_dir = dirname(__file__)
log = logz.simple("test_torch.log")
log = log("test.torch.recal")
log.info("new test start")
from ..az import nreshape
class MAModel(nn.Module):
    def __init__(self, ma):
        super().__init__()
        self.ma = ma
    def forward(self, input):
        return self.ma(input, input, input)[0]
def unit(din, num_ln, num_attrn, num_conv, num_heads=8, k_size = 3, shape_conv = None, shape_out = None, dropout_rate=0):
    '''
        shape_conv: [channel, width, height]
    '''
    nets = []
    for i in range(num_ln):
        nets.append(nn.Linear(din, din))
        if dropout_rate>0:
            nets.append(nn.Dropout(dropout_rate))
        nets.append(nn.LeakyReLU())
    for i in range(num_attrn):
        net = MAModel(nn.MultiheadAttention(din,num_heads,bias=True,batch_first=True))
        if dropout_rate>0:
            nets.append(nn.Dropout(dropout_rate))
        nets+=[net, nn.LeakyReLU()]
    if num_conv>0:
        assert k_size%2==1
        padding = (k_size-1)>>1
        ch = shape_conv[0]
        nets.append(nreshape.reshape(shape_conv,1))
        for i in range(num_conv):
            net = nn.Conv2d(ch, ch, k_size, padding=padding)
            if dropout_rate>0:
                nets.append(nn.Dropout(dropout_rate))
            nets+=[net, nn.LeakyReLU()]
        nets.append(nreshape.reshape(shape_out,1))
    return nn.Sequential(*nets)

def gen(num, train_batch, test_batch, seq_n, din, num_ln, num_attrn, num_conv, num_heads=8, k_size = 3, shape_conv = None, shape_out = None, dropout_rate=0):
    if num_conv>0:
        assert seq_n*din == az.mul(shape_conv)
        assert seq_n*din == az.mul(shape_out)
    nets = [
        unit(din, num_ln, num_attrn, num_conv, num_heads, k_size, shape_conv, shape_out,dropout_rate) for i in range(num)
    ]
    model = nn.Sequential(*nets)
    train_data = torch.randn(train_batch, seq_n, din)
    test_data = torch.randn(test_batch,seq_n, din)
    return model, train_data, test_data

def eval(model, data):
    model.eval()
    with torch.no_grad():
        out = model(data)
    out = (out-data)**2
    #out = out.mean()
    return out.sum()
    return out.mean(axis=1)
def wrap_fc(fc, *a, **b):
    return fc(*a, **b)
def train(model, data, loop, lr=0.0001, show_epoch=100, cal_obj= wrap_fc, spt = False):
    opt = optim.Adam(model.parameters(), lr=lr)
    log.info(f"TRAIN")
    fc_loss = nn.MSELoss()
    fc_loss = lambda out,tgt:((out-tgt)**2).mean()
    curr=time.time()
    print(f"spt: {spt}")
    model.train()
    for i in range(loop):
        opt.zero_grad()
        if spt:
            print(f"do spt")
            out = data
            for net in model:
                out = cal_obj(net, out)
        else:
            out = cal_obj(model, data)
        loss = fc_loss(out, data)
        loss.backward()
        if i%show_epoch==0 or i == loop-1:
            log.info(f"loss[{i}/{loop}]: {loss}, {type(loss)}")
        opt.step()
    sec = time.time()-curr
    log.info(f"train loop: {loop}, time cost: {sec} sec")


def save(fp):
    global model, train_data, test_data
    eval_train = eval(model, train_data)
    eval_test = eval(model, test_data)
    print(f"save: train: {train_data.mean(), eval_train.mean()}, test: {test_data.mean(), eval_test.mean()}")
    dv.xsave(fp, model=model, trainx=train_data, testx=test_data)

def load(fp):
    if not isfile(fp):
        print(f"[WRAN] load fp '{fp}' is not exist and will not be load")
        return
    assert isfile(fp), f"data file not exist: {fp}"
    global model, train_data, test_data
    eval_train = eval(model, train_data)
    eval_test= eval(model, test_data)
    print(f"before load: train: {train_data.mean(), eval_train.mean()}, test: {test_data.mean(), eval_test.mean()}")
    obj = dv.xload(fp, model=model, trainx=train_data, testx=test_data)
    model, train_data, test_data = obj.model, obj.trainx, obj.testx
    eval_train = eval(model, train_data)
    eval_test = eval(model, test_data)
    print(f"load: train: {train_data.mean(), eval_train.mean()}, test: {test_data.mean(), eval_test.mean()}")




from buildz import args as argx, xf
args = xf.loads(r"""
[order, fp]
{
g:gpu
f:fp
fp:filepath
cf: conf_path
c:cuda
cuda:gpu
r:dropout_rate
}
[g,gpu,spt]
""")
conf_path = join(curr_dir, "test_recal_cuda.js")
fetch = argx.Fetch(*args)
conf = fetch()
conf_path = conf.get("conf_path", conf_path)
if not isfile(conf_path):
    conf_path = join(curr_dir, conf_path)
base_conf = xf.loadf(conf_path)
base_conf.update(conf)
conf = base_conf
fp = conf.get("filepath", "init.dt")
order = conf.get("order", "save")
gpu = conf.get("gpu", False)
lr=0.001
lr = float(conf.get("lr", 0.001))
train_loop = int(conf.get("train_loop", 2000))
show_epoch = int(conf.get("show_epoch", 100))
max_remains = int(conf.get("max_remains", 10))
cache_size = conf.get("cache_size", "1T")
model, train_data, test_data = gen(
    int(conf.get("num", 3)), 
    int(conf.get("train_batch", 10)), 
    int(conf.get("test_batch", 3)), 
    int(conf.get("seq_n", 16)), 
    int(conf.get("din", 256)), 
    int(conf.get("num_ln", 3)), 
    int(conf.get("num_attrn", 0)), 
    int(conf.get("num_conv", 0)), 
    int(conf.get("num_heads", 4)), 
    int(conf.get("k_size", 3)), 
    conf.get("shape_conv", (4,32,32)), 
    conf.get("shape_out", (16, 256)),
    float(conf.get("dropout_rate", 0.0))
)
print(f"model: {len(model)}, size: {az.fmt_sz(dv.sizes(model))}")
if order=='save':
    log.info(f"save to: {fp}")
    save(fp)
    log.info(f"done save")
    exit(0)
class Check(nn.Module):
    def __init__(self, net):
        super().__init__()
        self.net =net
    def forward(self, *a, **b):
        return checkpoint(self._forward, *a, use_reentrant=False, **b)
    def _forward(self, *a, **b):
        return self.net(*a, **b)
def fc_check(fc, *a, **b):
    return checkpoint(fc, *a, use_reentrant=False, **b)
log.info("conf:", conf)
spt = int(conf.get("spt", 0))
sptable=False
if order == "train":
    cal_obj = wrap_fc
elif order == "trainx" or order=="cachex" or order == 'testx':
    cal_obj = recal.ReCal(cache_size)
elif order == 'trainxr':
    cal_obj = recal.recal_with_rngs(cache_size)
elif order=='trainc':
    cal_obj = fc_check
elif order == 'traincc':
    cal_obj = wrap_fc
elif order == "trainxs" or order=="cachexs" or order == 'testxs':
    sptable = True
    cal_obj = recals.ReCals(cache_size,max_remains=max_remains)
elif order == 'trainxsr':
    sptable = True
    cal_obj = recals.recals_with_rngs(cache_size,max_remains=max_remains)
elif order=='size':
    size = dv.sizes(model)
    print(f"model size: {az.fmt_sz(size)}")
    exit()
else:
    assert False
if not sptable:
    spt = False
spt = bool(spt)
if order=="cachex":
    out = cal_obj(model, train_data)
    print(f"caches:", cal_obj.cache_size(1))
    exit(0)
if order == "cachexs":
    cache_size, max_unit = cal_obj.analyze(model, train_data)
    print(f"total cache size: {az.fmt_sz(cache_size)}, max_unit_size: {az.fmt_sz(max_unit)}")
    exit(0)
if order=='testx' or order=='testxs':
    print(f"try train")
    train(model, train_data, 1, lr, show_epoch, cal_obj, spt)
    print(f"trainable")
    exit(0)

load(fp)
if order == 'traincc':
    model = Check(model)
if gpu:
    log = log("test.torch.recal.cuda")
    log.info("use cuda")
    model = model.cuda()
    train_data = train_data.cuda()
    test_data = test_data.cuda()

log.info(f"cal_obj: {cal_obj}, model: {type(model)}")
train(model, train_data, train_loop, lr, show_epoch, cal_obj, spt)

# log.info(f"test_data: {test_data}")
vals = eval(model, train_data)
log.info(f"eval train: {vals.mean()}")

vals = eval(model, test_data)
log.info(f"eval test: {vals.mean()}")
"""

生成一个模型和训练/测试数据，存储成文件

非recal模式，展示测试数据计算结果，进行数据训练，展示loss值，展示测试数据结果

recal模式，展示测试数据计算结果，进行数据训练，展示loss值，展示测试数据结果

python -m buildz.gpu.test.test_recal_cuda save





8 7 8
5 4 5
2 1 2

0 1 2 3 4 5 6 7 8 9
1     1     1     1 



0 1 2 3 4 5 6 7 8 9
1             1 1 1
"""


from buildz.gpu.torch import recal, dv

import torch
from torch import nn, optim
from buildz import log as logz
log = logz.simple("test_torch.log")
log = log("test.torch.hook")
log.info("new test start")
def gen():
    nets = []
    for i in range(3):
        tmp = [
            nn.Linear(3,4), nn.LeakyReLU(), 
            nn.Linear(4,3), nn.LeakyReLU(), 
            nn.Linear(3,3), nn.LeakyReLU()
        ]
        nets.append(nn.Sequential(*tmp))
    nets = [nets[0], nets[1], nets[2], nets[2], nets[1]]
    model = nn.Sequential(*nets)
    train_data = torch.randn(50, 3)
    test_data = torch.randn(2,3)
    return model, train_data, test_data

def eval(model, data):
    with torch.no_grad():
        out = model(data)
    return out.mean(axis=1)
def wrap_fc(fc, *a, **b):
    return fc(*a, **b)
def train(model, data, loop, lr=0.0001, show_epoch=100, cal_obj= wrap_fc):
    opt = optim.Adam(model.parameters(), lr=lr)
    log.info(f"FORWARD\n\n")
    fc_loss = nn.MSELoss()
    for i in range(loop):
        opt.zero_grad()
        out = cal_obj(model, data)
        loss = fc_loss(out, data)
        loss.backward()
        if i%show_epoch==0 or i == loop-1:
            log.info(f"loss: {loss}, {type(loss)}")
        opt.step()


def save(fp):
    global model, train_data, test_data
    eval_train = eval(model, train_data)
    eval_train = eval(model, test_data)
    print(f"save: train: {train_data.mean(), eval_train.mean()}, test: {test_data.mean(), eval_train.mean()}")
    dv.xsave(fp, model=model, trainx=train_data, testx=test_data)

def load(fp):
    global model, train_data, test_data
    eval_train = eval(model, train_data)
    eval_train = eval(model, test_data)
    print(f"before load: train: {train_data.mean(), eval_train.mean()}, test: {test_data.mean(), eval_train.mean()}")
    obj = dv.xload(fp, model=model, trainx=train_data, testx=test_data)
    model, train_data, test_data = obj.model, obj.trainx, obj.testx
    eval_train = eval(model, train_data)
    eval_train = eval(model, test_data)
    print(f"load: train: {train_data.mean(), eval_train.mean()}, test: {test_data.mean(), eval_train.mean()}")


model, train_data, test_data = gen()

import sys
order = sys.argv[1]
if order=='save':
    save("init.dt")
    exit(0)
elif order == "train":
    cal_obj = wrap_fc
elif order == "trainx":
    # cal_obj = recal.ReCal(20612//3)
    cal_obj = recal.ReCal("6.78K")
else:
    assert False
load("init.dt")
lr=0.001
batch=2
train_loop = 2000
show_epoch = 100
log.info(f"cal_obj: {cal_obj}")
train(model, train_data, train_loop, lr, show_epoch, cal_obj)
log.info(f"test_data: {test_data}")
vals = eval(model, test_data)
log.info(f"eval: {vals}")

exit(0)

cal_obj = recal.ReCal(20612//2)
lr=0.001
batch=2
train_loop = 2000
show_epoch = 100
train(model, train_data, train_loop, lr, show_epoch, cal_obj)
log.info(f"test_data: {test_data}")
vals = eval(model, test_data)
log.info(f"eval: {vals}")
"""

生成一个模型和训练/测试数据，存储成文件

非recal模式，展示测试数据计算结果，进行数据训练，展示loss值，展示测试数据结果

recal模式，展示测试数据计算结果，进行数据训练，展示loss值，展示测试数据结果

python -m buildz.gpu.test.test_recal
"""
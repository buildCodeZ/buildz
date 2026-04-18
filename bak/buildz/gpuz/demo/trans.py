


from buildz.gpuz.az import *


from buildz import xf, fz

from torch import nn
import torch
din =4096*4
batch=10240
loop=6
# data = torch.randn(batch, din, pin_memory=True)requires_grad=False
datas = [torch.randn(batch, din, pin_memory=True) for i in range(loop)]
n = batch*din
size = n*4
print(f"data: {fmt_sz(batch*din*loop)}")
import time
curr=time.time()
for i in range(loop):
    data = datas[i]
    data=data.cuda()
    del data
    # data=data.cpu()
sec = time.time()-curr
print(f"time cost: {sec}/{loop}")
assert sec>0
speed = size*loop/(sec+1e-10)
print(f"speed: {fmt_sz(speed)}")

"""
python -m buildz.gpuz.demo.trans
"""



from buildz.gpuz.az import *


from buildz import xf, fz

from torch import nn
import torch
din =4096*4
batch=10240
loop=10
data = torch.randn(batch, din, pin_memory=True)
n = batch*din
size = n*4
print(f"data: {fmt_sz(batch*din*loop)}")
import time
curr=time.time()
for i in range(loop):
    data = data
    data=data.cuda()
    data=data.cpu().contiguous()
sec = time.time()-curr
print(f"time cost: {sec}/{loop}")
assert sec>0
speed = size*loop/(sec+1e-10)
print(f"speed: {fmt_sz(speed)}")

"""
python -m buildz.gpuz.demo.trans2
"""
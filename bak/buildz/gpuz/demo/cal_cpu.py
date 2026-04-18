


from buildz.gpuz.az import *


from buildz import xf, fz

from torch import nn
import torch
din =4096*2
dout = 4096*2
batch=10240
az_nets = []
nets = []
for i in range(5):
    az_nets.append(Linear(din,dout))
    nets.append(nn.Linear(din,dout))
az_nets = Nets(*az_nets)
nets = nn.Sequential(*nets)
data = torch.randn(batch, din)
print(f"data: {fmt_sz(batch*din)}")
print(f"net size: {fmt_sz(az_nets.size(4))}")
print(f"cache: {fmt_sz(az_nets.cache(data.size(),4))}")
print(f"cal: {fmt_sz(az_nets.cal(data.size()))}")
print("done")
import time
# nets=nets.cuda()
# data=data.cuda()
loop=5
out = data
curr=time.time()
with torch.no_grad():
    for i in range(loop):
        out = nets(out)
sec = time.time()-curr
print(f"time cost: {sec}/{loop}")
assert sec>0
speed = az_nets.cal(data.size())*loop/(sec+1e-10)
print(f"speed: {fmt_sz(speed)}")

"""
python -m buildz.gpuz.demo.test_cal
"""
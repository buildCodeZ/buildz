


from buildz.gpuz.az import *
# from buildz.gpuz.az.nreshape import reshape

from buildz import xf, fz

# from torch import nn
# import torch
import os
dp = os.path.dirname(__file__)
fp = os.path.join(dp, "az.js")
conf = xf.loadf(fp)
speed = conf.get("cal", {})
speed_gpu = nsize(speed.get("gpu", "10T"))
speed_cpu = nsize(speed.get("cpu", "500G"))
trans = conf.get("trans", {})
trans_mem = nsize(trans.get("gpu2mem", "1G"))
def unit(din):
    # batch, seq_n, din
    nets = []
    #nets.append(MultiAttrn(din, din, 8))
    #nets.append(MultiAttrn(din, din, 8))
    nets.append(Linear(din,din))
    nets.append(Linear(din,din))
    nets.append(Linear(din,din))
    return nets

def conv_unit(ksize, ch_in, ch_out, reshape):
    # batch, seq_n, din
    nets = []
    nets.append(Reshape(reshape))
    if type(ksize)!={list, tuple}:
        ksize = [ksize, ksize]
    nets.append(Conv(2, ch_in, ch_out, ksize, 1, 1, [k//2 for k in ksize]))
    batch, ch, w, h = reshape
    outshape = [batch, ch_out, w, h]
    nets.append(Reshape(outshape))
    #nets.append(MultiAttrn(din, din, 8))
    nets.append(Linear(din,din))
    return nets

din =4096
din=256
batch=500000000
seq_n=1024
az_nets = []
for i in range(50):
    #az_nets+=conv_unit(3, 4, 4, [batch, 4, 32, 32])
    az_nets+=unit(din)

az_nets = Nets(*az_nets)
data_shape = [batch, din]

data_size = mul(data_shape)*4
data_trans = data_size/trans_mem
print(f"data: {fmt_sz(data_size)}, data_trans: {data_trans:.3f} sec")
net_size = az_nets.size(4)
net_trans = net_size/trans_mem
print(f"net size: {fmt_sz(net_size)}, net_trans: {net_trans:.3f} sec")
cache_size = az_nets.cache(data_shape,4)
cache_trans = cache_size/trans_mem
print(f"cache: {fmt_sz(cache_size)}, cache_trans: {cache_trans:.3f} sec")
cal_amount = az_nets.cal(data_shape)
cal_gpu = cal_amount/speed_gpu
cal_cpu = cal_amount/speed_cpu
print(f"cal: {fmt_sz(cal_amount)}, cal_gpu: {cal_gpu:.3f} sec, cal_cpu: {cal_cpu:.3f} sec")
print("done")
"""
python -m buildz.gpuz.demo.az
"""

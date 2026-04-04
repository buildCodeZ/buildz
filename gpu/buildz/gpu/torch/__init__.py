#coding=utf-8
try:
    import torch
except ModuleNotFoundError as exp:
    print(f"package pytorch is required, try pip install torch to download cpu version, or visit pytorch.org to download gpu version")
    raise exp
__version__="0.0.1"

__author__ = "Zzz, emails: 1174534295@qq.com, 1309458652@qq.com"
# 小号多

from .middle_cache import MiddleCache
# from .recal import ReCal, recal_with_rngs
from .recals import ReCals, recals_with_rngs

'''
模型训练显存不足解决方案
两个方案：
1，用内存当缓存（MiddleCache），测试效果不好，传输太耗时间
2，forward的时候在显存不够的时候丢掉前面的缓存，后面重新计算(ReCals)，测试效果不错，用起来也方便
    如果网络层包括随机数（比如dropout层），为了重新计算的时候dropout层计算的结果一样，建议用recals_with_rngs，其会在计算前缓存随机数种子，重新计算的时候使用之前的随机数种子
    
    ReCals实现后才发现有个torch.utils.checkpoint
    和checkpoint区别：
        checkpoint需要手动设置哪些网络层调用checkpoint，在这些网络层设置checkpoint
        ReCals是设置一个最大缓存大小，自动抛弃缓存和反向梯度的时候重新计算
        逻辑上的区别还没看

代码里还有个recal，是之前写的，只是用来和recals做时间对比


recals额外增加的计算开销分析：
1，从网上查的，backward的计算量约等于forward的2倍
2，recals只增加forward的计算开销
3，假设每个网络层计算量相同（实际上不同类型网络层（卷积，注意力，全连接）的计算量不同）

假设原来forward计算量是n，原计算量是forward和backward的总和=3n

如果设置缓存上限是需要缓存的数据量的一半，则增加0.5个forward计算量，总共3.5n，是原计算量的1.167倍

如果设置缓存上限是需要缓存的数据量的1/4，则[0.75,1.0]的缓存直接用，[0.5, 0.75]的缓存需要0.75n的额外计算量，[0.25,0.5]的缓存需要0.5n的额外计算量，[0, 0.25]的缓存需要0.25的额外计算量，额外计算量共1.5n，总计算量为4.5n，是原计算量的1.5倍


| 缓存设置上限占缓存的总量的比例 | 计算量 | 额外计算量开销 |
|     不限制（不使用recals）    |  3n   |       0%      |
|           50%                |  3.5n |      16.7%    |
|           25%                |  4.5n |      50%      |
|           12.5%              |  6.5n |     116.7%    |


模型训练的时候，模型缓存占用的显存一般远大于模型占用的显存

参考代码1:

from buildz.gpu import az,torch as torchz

cache_size = az.nsize("4G")
# 或者cache_size=4*(1024**3)
opt = ...
model = ...
fc_loss = ...

recals = torchz.recals_with_rngs(cache_size)
for inputs, targets in dataloader:
    opt.zero_grad()
    # 如果原来是out=model(...)，就改成out=recals(model, ...)
    out = recals(model, inputs)
    loss = fc_loss(out, targets)
    loss.backard()
    opt.step()


参考代码2:

如果有多张显卡，或者一部分在内存，一部分在显存，对每一张显卡都要创建一个recals，内存的如果内存不够可以也创建一个，内存足够可以不管
注：只创建一个recals也可以使用，但recals只会控制被它调用的模型的缓存的总量，不会在乎这些缓存是保存在内存还是不同显卡的显存，这种缓存限制没有意义

假设两张显卡a和b，再加上用cpu和内存计算，并且第一张显卡存两个模型
model_cuda_a0 = ...
model_cpu = ...
model_cuda_a1 = ...
model_cuda_b = ...

原代码

for ...:
    ...
    inputs=inputs.to(device_cuda_a)
    targets=targets.to(device_cuda_b)
    middle_cuda_a0 = model_cuda_a0(inputs).cpu()
    middle_cpu = model_cpu(middle_cuda_a0).to(device_cuda_a)
    middle_cuda_a1 = model_cuda_a1(middle_cpu).to(device_cuda_b)
    out = model_cuda_b(middle_cuda_a1)
    loss = fc_loss(out, targets)
    loss.backward()
    ...

修改后

# 假设两张显卡都最多只允许缓存4G数据
# 假设两张显卡的编号是id_cuda_a, id_cuda_b（显卡编号是从0开始的，0,1,2 ...）
#   注：如果不知道显卡编号，也可以不传，但这样会默认存所有显卡的随机数种子（一个随机数种子816字节）
recals_cuda_a = torchz.recals_with_rngs(az.nsize("4G"), id_cuda_a)
recals_cuda_b = torchz.recals_with_rngs(az.nsize("4G"), id_cuda_b)
for ...:
    ...
    inputs=inputs.to(device_cuda_a)
    targets=targets.to(device_cuda_b)
    middle_cuda_a0 = recals_cuda_a(model_cuda_a0, inputs).cpu()
    middle_cpu = model_cpu(middle_cuda_a0).to(device_cuda_a)
    middle_cuda_a1 = recals_cuda_a(model_cuda_a1, middle_cpu).to(device_cuda_b)
    out = recals_cuda_b(model_cuda_b, middle_cuda_a1)
    loss = fc_loss(out, targets)
    loss.backward()
    ...

'''

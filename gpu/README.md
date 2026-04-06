# buildz.gpu.torch
declaration:
Codes of this project are not allowed to be used for AI training or any other form of machine learning processes.

声明:
禁止将本项目的代码用于ai训练
## 1，简介

用python写的gpu模型训练相关工具

注：后面测试发现pytorch的torch.utils.checkpoint在一样减少训练缓存的情况下性能更好，只是配置更复杂些，建议直接用checkpoint

## 2，提供方法
利用重复计算节省显存模型缓存空间：
```
buildz.gpu.torch.recals_with_rngs(cache_limit_size, gpu_devices="all")
```
#### 原理：
设置模型训练缓存的最大上限，前向计算(forward)的时候，如果缓存达到上限，就把最前面存的缓存删了，反向计算(backward)的时候，检测到缓存不存在就重新启动前向计算直到生成到当前缺失缓存的节点。

如果假设模型里每层网络的计算开销是一样的，网络的反向计算的计算量是前向计算的2倍，缓存最大上限设置成实际需要缓存大小的50%，会增加16.7%的计算开销；设置为25%，会增加50%的计算开销；设置为12.5%，会增加116.7%的计算开销，也就是训练时间变成两倍多。实际不同网络层的计算开销不一样，需要使用者自己测试。

注1：写完才发现pytorch有个torch.utils.checkpoint，是类似的作用（重计算），但它是更细致的静态的网络层的调用，直接设置哪个网络层不存储缓存，可以精确地去手动设置那些计算量少但缓存大的网络层为重计算，缺点是配置麻烦，但除了配置麻烦貌似基本没缺点了，性能也更好，建议直接用checkpoint

注2：函数名里的rngs表示会调用torch.cuda.get_rng_state/torch.get_rng_state和torch.cuda.set_rng_state/torch.set_rng_state获取和重置pytorch的随机数的种子(1KB以内的内存数据，不占显存)
#### 输入参数：
    cache_limit_size: 最大缓存大小限制(字节)
    gpu_devices: 需要在计算前存随机数种子的显卡设备索引/索引列表，可选值：
        "cuda": 所有显卡，不清楚用的哪张显卡就用这个或all
        "all": 默认值，所有显卡和cpu，不清楚用的哪张显卡就用这个或cuda
        "cpu": cpu
        "none": 不存随机数种子（如果模型里没有如dropout之类需要用随机数的网络层，可以不存随机数种子）
        整数: 显卡索引，从0开始，比如有两张显卡，就是存在显卡索引0和1，另外-1代表cpu
        列表: 显卡索引列表，例: [0,1,2]
        torch.Tensor: 会调用torch.Tensor.get_device()获取显卡索引
#### 用法示例：
1）分析模型训练需要使用的缓存大小，不实际训练：
```
from buildz.gpu.torch import recals_with_rngs
recals = recals_with_rngs(-1)
model.train()
total_cache_size, unit_max_cache_size = recals.analyze(model, inputs)

recals.analyze会在模型forward的时候，存一个缓存删一个缓存，只统计缓存大小
返回的两个数据说明如下:
    total_cache_size: 模型用到的总缓存大小(byte)
    unit_max_cache_size: 模型里单个网络层的最大缓存大小(byte)（这里的网络层是指最小的网络层单元，比如nn.Sequential(nn.Linear(10,10), nn.Linear(10,10))，是两个nn.Linear网络层，而不是一个nn.Sequential网络层）
```
2）训练示例1：
```
from buildz.gpu.torch import recals_with_rngs
...
# 假设设置4GB缓存上限
cache_limit_size=4*(1024**3)
recals = recals_with_rngs(cache_limit_size)
...
# 代替原代码的: output = model(inputs0, inputs1, labels = labels)
#   recals(fc, *a, **b)等于在recals里调用fc(*a, **b)
output = recals(model, inputs0, inputs1, labels = labels)
...
```


3）训练示例2：
原代码：
```
model.train()
for input, target in dataloader:
    opt.zero_grad()
    output = model(input)
    loss = fc_loss(output, target)
    loss.backward()
    opt.step()
```

修改后代码：

```
# 修改1：创建recals
from buildz.gpu.torch import recals_with_rngs
# 假设设置4GB缓存上限
cache_limit_size=4*(1024**3)
recals = recals_with_rngs(cache_limit_size)

model.train()
for input, target in dataloader:
    opt.zero_grad()
    # 修改2，使用recals
    output = recals(model,input)
    loss = fc_loss(output, target)
    loss.backward()
    opt.step()
```
4）训练示例3：

如果模型做了切分，在显卡和cpu上分别计算，或者在不同显卡上计算，需要为每张需要限制缓存的显卡创建一个recals。因为每个recals只会控制被它调用的模型的缓存总量，不管这些模型的缓存是保存在同一张显卡还是不同显卡，还是有部分在显卡，有部分在内存，放同一个recals对象里运行是可以正常运行，但这样用recals没有意义

假设三张显卡a、b和c，显卡a和b要分别限制缓存为6GB和4GB，同时还在cpu上计算:

原代码:
```
for input, target in dataloader:
    ...
    input = input.to(device_a)
    target = target.to(device_c)
    middle_a0 = model_cuda_a0(input)
    middle_cpu = model_cpu(middle_a0.cpu())
    middle_a1 = model_cuda_a1(middle_cpu.to(device_a))
    middle_b = model_cuda_b(middle_a1.to(device_b))
    output = model_cuda_c(middle_b.to(device_c))
    loss = fc_loss(output, target)
    loss.backward()
    ...

```
修改后代码：
```
# 修改1：创建recals
from buildz.gpu.torch import recals_with_rngs
# 这里device_a和device_b也可以不传入，反正一张显卡也就多存1KB的内存
recals_a = recals_with_rngs(6*(1024**3), device_a)
recals_a = recals_with_rngs(4*(1024**3), device_b)

for input, target in dataloader:
    ...
    input = input.to(device_a)
    target = target.to(device_c)
    # 修改2，使用recals
    middle_a0 = recals_a(model_cuda_a0, input)
    middle_cpu = model_cpu(middle_a0.cpu())
    # 修改3，使用recals
    middle_a1 = recals_a(model_cuda_a1, middle_cpu.to(device_a))
    # 修改4，使用recals
    middle_b = recals_b(model_cuda_b, middle_a1.to(device_b))
    output = model_cuda_c(middle_b.to(device_c))
    loss = fc_loss(output, target)
    loss.backward()
    ...
```

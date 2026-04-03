#coding=utf-8
try:
    import torch
except ModuleNotFoundError as exp:
    print(f"package pytorch is required, try pip install torch to download cpu version, or visit pytorch.org to download other version")
    pass
__version__="0.0.1"

__author__ = "Zzz, emails: 1174534295@qq.com, 1309458652@qq.com"
# 小号多

from .middle_cache import MiddleCache
from .recal import ReCal, recal_with_rngs
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

代码里还有个recal，是之前写的，只适合单个设备训练，并且loss.backward之前只能调用一次forward，recals做了优化
'''

// unit num
num=10
train_batch: 10
test_batch: 3
"seq_n"= 256
"din"= 512
"num_ln"= 10
"num_attrn"= 3
"num_conv"= 3
"num_heads"= 4
"k_size"= 3
"shape_conv"= (32,64,64)
"shape_out"= (256, 512)
dropout_rate:0.2
lr: 0.0003
cache_size: 2.5G
train_loop = 100
show_epoch = 10
gpu: true
order: save
filepath: recals_cuda_r.dt
max_remains: 10


/*
python -m buildz.gpu.test.recals --cf recals_cuda_r.js

实测数据：
十层模型，每层10个线性层，3个注意力，3个卷积
模型大小223MB，缓存总需求4.9GB，单个网络层最大缓存需求10MB
model: 10, size: 223.605M
total cache size: 4.904G, max_unit_size: 10.000M


不用recals
[INFO] 2026-04-06 08:26:16 [test.torch.recal.cuda] train loop: 100, time cost: 26.53198480606079 sec

2.5GB(50%)缓存上限的recals
[INFO] 2026-04-06 08:27:33 [test.torch.recal.cuda] train loop: 100, time cost: 29.631866931915283 se
c
>>> 29.631866931915283/26.53198480606079-1
0.11683566640466259

1.25GB(25%)缓存上限的recals
[INFO] 2026-04-06 08:29:31 [test.torch.recal.cuda] train loop: 100, time cost: 35.88364338874817 sec

35.88364338874817/26.53198480606079-1
0.3524673578341242

0.625GB(12.5%)缓存上限的recals
[INFO] 2026-04-06 09:03:51 [test.torch.recal.cuda] train loop: 100, time cost: 48.930402517318726 se

>>> 48.930402517318726/26.53198480606079-1
0.8442043772820715
*/
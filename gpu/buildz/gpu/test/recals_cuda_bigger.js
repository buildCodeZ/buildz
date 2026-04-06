// unit num
num=10
segments: 10
train_batch: 1
test_batch: 3
"seq_n"= 8192
"din"= 1024
"num_ln"= 0
"num_attrn"= 1
"num_conv"= 0
"num_heads"= 4
"k_size"= 3
"shape_conv"= (32,64,64)
"shape_out"= (256, 512)
dropout_rate:0.2
lr: 0.0003
cache_size: 3.5G
train_loop = 1
show_epoch = 10
gpu: true
order: save
filepath: recals_cuda_bigger.dt
max_remains: 10


/*
python -m buildz.gpu.test.recals --cf recals_cuda_ma.js

实测数据：
十层模型，每层1个线性层，3个注意力，1个卷积
模型大小130MB，缓存总需求2.32GB，单个网络层最大缓存需求10MB
model: 10, size: 130.607M
total cache size: 2.324G, max_unit_size: 10.000M


不用recals
[INFO] 2026-04-06 08:38:29 [test.torch.recal.cuda] train loop: 100, time cost: 14.884939670562744 sec

1.16GB(50%)缓存上限的recals
[INFO] 2026-04-06 08:39:22 [test.torch.recal.cuda] train loop: 100, time cost: 16.8947594165802 sec
>>> 16.8947594165802/14.884939670562744-1
0.1350237078885972

0.58GB(25%)缓存上限的recals
[INFO] 2026-04-06 08:40:15 [test.torch.recal.cuda] train loop: 100, time cost: 21.16289734840393 sec

21.16289734840393/14.884939670562744-1
0.42176574556474766

0.29GB(12.5%)缓存上限的recals
[INFO] 2026-04-06 08:42:41 [test.torch.recal.cuda] train loop: 100, time cost: 29.59679412841797 sec
>>> 29.59679412841797/14.884939670562744-1
0.9883717894369555
*/
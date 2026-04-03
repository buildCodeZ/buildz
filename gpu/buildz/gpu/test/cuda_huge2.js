// unit num
num=30
train_batch: 10
test_batch: 3
"seq_n"= 256
"din"= 512
"num_ln"= 30
"num_attrn"= 0
"num_conv"= 0
"num_heads"= 4
"k_size"= 3
"shape_conv"= (32,64,64)
"shape_out"= (256, 512)
lr: 0.0001
cache_size: 3G //1T//90M
train_loop = 10
show_epoch = 1
gpu: true
order: save
filepath: huge2.dt
// unit num
num=10
train_batch: 10
test_batch: 3
"seq_n"= 1024//256*16
// "seq_n"= 256
"din"= 512
"num_ln"= 10
"num_attrn"= 3
"num_conv"= 3
"num_heads"= 4
"k_size"= 3
"shape_conv"= (32,64,256)
"shape_out"= (1024, 512)
// "shape_conv"= (32,64,64)
// "shape_out"= (256, 512)
dropout_rate:0.2
lr: 0.0003
cache_size: 4G //1T//90M
// cache_size: 1G
train_loop = 3
show_epoch = 1
gpu: true
order: save
filepath: cuda_mini_rate.dt
max_remains: 10


/*
python -m buildz.gpu.test.test_recal_cuda --cf cuda_mini_rate.js cachexs
*/
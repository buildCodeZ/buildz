// unit num
num=21
train_batch: 10
test_batch: 3
"seq_n"= 1
"din"= 512
"num_ln"= 30
"num_attrn"= 0
"num_conv"= 0
"num_heads"= 4
"k_size"= 3
"shape_conv"= (32,64,64)
"shape_out"= (256, 512)
dropout_rate:0.15
lr: 0.0003
cache_size: 300M //1T//90M
train_loop = 100
show_epoch = 10
gpu: true
order: save
filepath: huge4.dt
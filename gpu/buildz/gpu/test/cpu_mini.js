// unit num
num=11
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
dropout_rate:0.0
lr: 0.0003
cache_size: 150M //1T//90M
train_loop = 10
show_epoch = 1
gpu: false
order: save
filepath: mini.dt

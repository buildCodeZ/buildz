
cal:{
    // 理论值
    // RTX4060: 15T
    // i7-13700H: 657G
    // 测试值
    RTX4060: 12T
    gpu: 12T
    i7-13700H: 500G
    cpu: 500G
}
trans: {
    gpu: 272G
    // PCIE4x8 2G*8，理论值
    // gpu_mem: 16G
    // 实际值，需要加上pin_memory=True标志，如torch.randn(..., pin_memory=True)，让内存分配连续才能达到
    // 
    gpu2mem: 10G
    // 实际训练数据，由于在内存里是分散存放的，拷贝到显存的速度更慢
    gpu2mem: 1.6G
    wifi6: 1.2G
}

// unit num
num=5
train_batch: 10
test_batch: 3
"seq_n"= 1024//256*16
"din"= 512
"num_ln"= 10
"num_attrn"= 3
"num_conv"= 3
"num_heads"= 4
"k_size"= 3
"shape_conv"= (32,64,256)
"shape_out"= (1024, 512)
dropout_rate:0.2
lr: 0.0003
cache_size: 4G //1T//90M
train_loop = 3
show_epoch = 1
gpu: true
order: save
filepath: cuda_mini_rate.dt
/*
python -m buildz.gpu.demo.az --cf az.js
*/
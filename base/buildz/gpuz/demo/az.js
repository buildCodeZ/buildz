
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

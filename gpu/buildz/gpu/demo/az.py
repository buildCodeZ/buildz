from buildz.gpu import az
from buildz import log as logz
from os.path import dirname, join, isfile
curr_dir = dirname(__file__)
def unit(din, num_ln, num_attrn, num_conv, num_heads=8, k_size = 3, shape_conv = None, shape_out = None, dropout_rate=0):
    '''
        shape_conv: [channel, width, height]
    '''
    nets = []
    for i in range(num_ln):
        nets.append(az.Linear(din, din))
        if dropout_rate>0:
            nets.append(az.Dropout(dropout_rate))
        nets.append(az.LeakyReLU())
    for i in range(num_attrn):
        net = az.MultiAttrn(din,din,num_heads,bias=True)
        if dropout_rate>0:
            nets.append(az.Dropout(dropout_rate))
        nets+=[net, az.LeakyReLU()]
    if num_conv>0:
        assert k_size%2==1
        padding = (k_size-1)>>1
        ch = shape_conv[0]
        nets.append(az.Reshape(shape_conv,1))
        for i in range(num_conv):
            net = az.Conv(2, ch, ch, k_size, padding=padding)
            if dropout_rate>0:
                nets.append(az.Dropout(dropout_rate))
            nets+=[net, az.LeakyReLU()]
        nets.append(az.Reshape(shape_out,1))
    return az.Nets(*nets)

def gen(num, train_batch, test_batch, seq_n, din, num_ln, num_attrn, num_conv, num_heads=8, k_size = 3, shape_conv = None, shape_out = None, dropout_rate=0):
    print(f"num: {num}")
    if num_conv>0:
        assert seq_n*din == az.mul(shape_conv)
        assert seq_n*din == az.mul(shape_out)
    nets = [
        unit(din, num_ln, num_attrn, num_conv, num_heads, k_size, shape_conv, shape_out,dropout_rate) for i in range(num)
    ]
    model = az.Nets(*nets)
    train_data = [train_batch, seq_n, din]
    test_data = [test_batch,seq_n, din]
    return model, train_data, test_data

from buildz import args as argx, xf
args = xf.loads(r"""
[order, fp]
{
g:gpu
cf: conf_path
r:dropout_rate
}
""")
conf_path = join(curr_dir, "az.js")
fetch = argx.Fetch(*args)
conf = fetch()
conf_path = conf.get("conf_path", conf_path)
if not isfile(conf_path):
    conf_path = join(curr_dir, conf_path)
base_conf = xf.loadf(conf_path)
base_conf.update(conf)
conf = base_conf
order = conf.get("order", "save")
train_loop = int(conf.get("train_loop", 2000))
show_epoch = int(conf.get("show_epoch", 100))
cache_size = conf.get("cache_size", "1T")
model, train_data, test_data = gen(
    int(conf.get("num", 3)), 
    int(conf.get("train_batch", 10)), 
    int(conf.get("test_batch", 3)), 
    int(conf.get("seq_n", 16)), 
    int(conf.get("din", 256)), 
    int(conf.get("num_ln", 3)), 
    int(conf.get("num_attrn", 0)), 
    int(conf.get("num_conv", 0)), 
    int(conf.get("num_heads", 4)), 
    int(conf.get("k_size", 3)), 
    conf.get("shape_conv", (4,32,32)), 
    conf.get("shape_out", (16, 256)),
    float(conf.get("dropout_rate", 0.0))
)
print(f"model: {az.fmt_sz(model.size(4))}")

speed = conf.get("cal", {})
speed_gpu = az.nsize(speed.get("gpu", "10T"))
speed_cpu = az.nsize(speed.get("cpu", "500G"))
trans = conf.get("trans", {})
trans_mem = az.nsize(trans.get("gpu2mem", "1G"))
az_nets = model
data_shape = train_data

data_size = az.mul(data_shape)*4
data_trans = data_size/trans_mem
print(f"data: {az.fmt_sz(data_size)}, data_trans: {data_trans:.3f} sec")
net_size = az_nets.size(4)
net_trans = net_size/trans_mem
print(f"net size: {az.fmt_sz(net_size)}, net_trans: {net_trans:.3f} sec")
cache_size = az_nets.cache(data_shape,4)
cache_trans = cache_size/trans_mem
print(f"cache: {az.fmt_sz(cache_size)}, cache_trans: {cache_trans:.3f} sec")
cal_amount = az_nets.cal(data_shape)
cal_gpu = cal_amount/speed_gpu
cal_cpu = cal_amount/speed_cpu
print(f"cal: {az.fmt_sz(cal_amount)}, cal_gpu: {cal_gpu:.3f} sec, cal_cpu: {cal_cpu:.3f} sec")
print("done")
"""
python -m buildz.gpu.demo.az
"""

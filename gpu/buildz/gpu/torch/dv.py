#
import torch
'''
SaveModel: 存取模型数据的简化
cpu, cuda: 指向torch设备实例
device: 有cuda就是cuda，否则cpu

'''
def save(fp, maps):
    SaveModel(**maps).save(fp)
def load(fp, maps):
    return SaveModel(**maps).load(fp)
def xsave(fp, **maps):
    SaveModel(**maps).save(fp)
def xload(fp, **maps):
    return SaveModel(**maps).load(fp)
class SaveModel(torch.nn.Module):
    '''
        存取模型数据的简化
            maps = {k1: 模型1, k2: 模型2, ...}
        存储:
            SaveModel(**maps).save(fp)
            或
            dv.save(fp, maps)
            或
            dv.savex(fp, **maps)
        读取:
            SaveModel(**maps).load(fp)
            或
            dv.load(fp, maps)
            或
            dv.loadx(fp, **maps)
    '''
    def __init__(self, **maps):
        super().__init__()
        objs = {}
        for k,v in maps.items():
            if hasattr(v, "state_dict"):
                setattr(self, k,v)
            else:
                objs["_"+k] = v
        self.objs = objs
    def save(self, fp):
        from buildz import fz
        fz.makefdir(fp)
        data = self.state_dict()
        objs = dict(self.objs)
        objs["data"] = data
        torch.save(objs, fp)
    def __getattr__(self, key):
        _key = "_"+key
        if _key in self.objs:
            return self.objs[_key]
        return super().__getattr__(key)
    def load(self, fp):
        import os
        if not os.path.isfile(fp):
            return None
        objs = torch.load(fp)
        data = objs.pop("data")
        self.load_state_dict(data)
        self.objs = objs
        return self
pass
cpu = torch.device('cpu')
cuda = None
if torch.cuda.is_available():
    cuda = torch.device('cuda')

device = cpu if cuda is None else cuda
dv = device
def cuda_mem():
    return torch.cuda.memory_allocated()

pass
def tsz(tensor):
    return tensor.element_size()*tensor.nelement()
def sizes(datas):
    if isinstance(datas, torch.Tensor):
        return tsz(datas)
    _type = type(datas)
    if _type not in {tuple, list, dict}:
        return 0
    rst = 0
    if _type==dict:
        for k,v in datas.items():
            rst+=sizes(k)+sizes(v)
    else:
        for it in datas:
            rst+=sizes(it)
    return rst

def make_fc(fc = None, cuda = False):
    if fc is None:
        fc = lambda x:torch.is_tensor(x)
        if cuda:
            _fc = fc
            fc = lambda x:_fc(x) and x.device.type=='cuda'
    return fc
def objs_mem(fc = None, cuda = False):
    import gc,torch
    total = 0
    fc = make_fc(fc, cuda)
    for obj in gc.get_objects():
        if fc(obj):
            while obj is not None:
                total+=tsz(obj)
                obj = obj.grad
    return total
def objs(fc = None, cuda = False):
    import gc,torch
    rst=[]
    fc = make_fc(fc, cuda)
    for obj in gc.get_objects():
        if fc(obj):
            rst.append(obj)
    return rst
gpu_mem = cuda_mem
#device = cpu
def clean():
    torch.cuda.empty_cache()
#
from . import fio
"""
col=1,as_map = 1
{
    a: [a1,a2,a3,...]
    b: [b1,b2,b3,...]
    ...
}

col=1, as_map=0
[
    [a1,a2,a3,...]
    [b1,b2,b3,...]
    ...
]

col=0,as_map = 1
[
    {a:a1,b:b1,...},
    {a:a2,b:b2,...},
    ...
]

col=0,as_map=0
[
    [a1,b1,...],
    [a2,b2,...],
    ...
]
"""
def to_csv(keys, datas, fp, col = True, as_map = False,coding="utf-8"):
    fio.makefdir(fp)
    rst = []
    if col:
        if as_map:
            datas = [datas[k] for k in keys]
        datas = list(zip(*datas))
    else:
        if as_map:
            datas = [[dt[k] for k in keys] for dt in datas]
    datas = [", ".join([str(v) for v in dt]) for dt in datas]
    rst = [", ".join(keys)]+datas
    rs = "\n".join(rst)
    fio.write(rs.encode(coding), fp)

pass

def from_csv(fp, col=True, as_map = False,coding="utf-8"):
    s = fio.read(fp).decode(coding)
    arr = s.split("\n")
    arr = [[v.strip() for v in k.split(",")] for k in arr if k.strip()!=""]
    keys = arr[0]
    datas = arr[1:]
    if col:
        outs = []
        for i in range(len(keys)):
            tmp = [k[i] for k in datas]
            outs.append(tmp)
        if as_map:
            outs = {k:arr for k,arr in zip(keys, datas)}
        datas = outs
    elif as_map:
        datas = [{k:v for k,v in zip(keys, dt)} for dt in datas]
    return keys, datas

pass
def wrap_cols(keys, cols):
    rst = {}
    for key, col in zip(keys, cols):
        rst[key] = col
    return rst

def init_merge_keys(keys_a, keys_b):
    rst = {}
    keys_b = {k:k for k in keys_b}
    for k in keys_a:
        rst[k] = []
    keys_b_ = {}
    for k,v in keys_b.items():
        while v in rst:
            v = v+"_"
        rst[v] = []
        keys_b_[k] = v
    keys_b = keys_b_
    return rst, keys_b
def merge_col_in(datas_a, datas_b, keys, keys_a = None, keys_b = None):
    if type(keys)==str:
        keys = [keys]
    if keys_a is None:
        keys_a = list(datas_a.keys())
    bak_a = keys_a
    keys_a = set(keys_a)
    if keys_b is None:
        keys_b = list(datas_b.keys())
    bak_b = keys_b
    keys_b = set(keys_b)
    l = len(datas_b[keys[0]])
    indexes = {}
    for i in range(l):
        vs = tuple([datas_b[k][i] for k in keys])
        indexes[vs] = i
    rst, keys_b = init_merge_keys(keys_a, keys_b)
    l = len(datas_a[keys[0]])
    for i in range(l):
        vs = tuple([datas_a[k][i] for k in keys])
        if vs not in indexes:
            continue
        j = indexes[vs]
        for k in keys_a:
            rst[k].append(datas_a[k][i])
        for k, k_ in keys_b.items():
            rst[k_].apepnd(datas_b[k][j])
    return rst, [keys_a, keys_b]

def merge_row_in(datas_a, datas_b, keys, keys_a = None, keys_b = None):
    if type(keys)==str:
        keys = [keys]
    if len(datas_a)*len(datas_b)==0:
        return []
    if keys_a is None:
        keys_a = list(datas_a[0].keys())
    bak_a = keys_a
    keys_a = set(keys_a)
    if keys_b is None:
        keys_b = list(datas_b[0].keys())
    bak_b = keys_b
    keys_b = set(keys_b)
    rst, keys_b = init_merge_keys(keys_a, keys_b)
    rst = []
    l = len(datas_b)
    indexes = {}
    for i in range(l):
        dt = datas_b[i]
        vs = tuple([dt[k] for k in keys])
        indexes[vs] = i
    l = len(datas_a)
    for i in range(l):
        dt = datas_a[i]
        vs = tuple([dt[k] for k in keys])
        if vs not in indexes:
            continue
        j = indexes[vs]
        tmp = {}
        for k in keys_a:
            tmp[k] = dt[k]
        dt = datas_b[j]
        for k, k_ in keys_b.items():
            tmp[k_] = dt[k]
        rst.append(tmp)
    keys_b = [v for k,v in keys_b.items()]
    return rst, [keys_a, keys_b]

    
def merge_in(datas_a, datas_b, keys, col = True, keys_a = None, keys_b = None):
    if col:
        return merge_col_in(datas_a, datas_b, keys, keys_a, keys_b)
    return merge_row_in(datas_a, datas_b, keys, keys_a, keys_b)
    
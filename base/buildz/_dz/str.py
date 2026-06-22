import struct
__all__=['val2bs', 'bs2val']
'''
基本数据（目前有bool,int,float,str,bytes,list,dict,tuple)转bytes，或bytes转基本数据
type_byte|val
str|num|val
bytes|num|val
list|num|...
dict|num|...
tuple|num|...
'''
def bs2none(bs):
    return None, 1
def none2bs(val):
    return t2bs[None]
def bs2false(bs):
    return False, 1
def false2bs(val):
    return t2bs[False]
def bs2true(bs):
    return True, 1
def true2bs(val):
    return t2bs[True]
def bs2int(bs):
    tmp = bs[1:1+4]
    val, =  struct.unpack(">I", tmp)
    return val, 1+4
def int2bs(val):
    val = struct.pack(">I", val)
    return t2bs[int]+val
def bs2float(bs):
    val, = struct.unpack(">d", bs[1:1+8])
    return val, 1+8
def float2bs(val):
    val = struct.pack(">d", val)
    return t2bs[float]+val

def bs2bytes(bs):
    num, = struct.unpack(">I", bs[1:1+4])
    val = bs[1+4:1+4+num]
    return val, 1+4+num
def bytes2bs(val):
    num = struct.pack(">I", len(val))
    return t2bs[bytes]+num+val
def bs2str(bs):
    val, num = bs2bytes(bs)
    return val.decode("utf-8"), num
def str2bs(val):
    tmp = bytes2bs(val.encode("utf-8"))
    return t2bs[str]+tmp[1:]
def bs2list(bs):
    num, = struct.unpack(">I", bs[1:1+4])
    rst = []
    uses = 5
    for i in range(num):
        val, use = _bs2val(bs[uses:])
        rst.append(val)
        uses+=use
    return rst, uses
def list2bs(val):
    num = struct.pack(">I", len(val))
    bs = t2bs[list]+num
    for it in val:
        bs+=val2bs(it)
    return bs
def bs2tuple(bs):
    rst, uses = bs2list(bs)
    return tuple(rst), uses
def tuple2bs(val):
    tmp = list2bs(val)
    return t2bs[tuple]+tmp[1:]
def bs2dict(bs):
    num, = struct.unpack(">I", bs[1:1+4])
    rst = {}
    uses = 5
    for i in range(num):
        key, use = _bs2val(bs[uses:])
        uses+=use
        val, use = _bs2val(bs[uses:])
        uses+=use
        #print(f"dict key: {key, type(key)}, val: {val, type(val)}")
        rst[key] = val
    return rst, uses
def dict2bs(val):
    num = struct.pack(">I", len(val))
    bs = t2bs[dict]+num
    for k,v in val.items():
        bs+=val2bs(k)+val2bs(v)
    return bs

fcs = {}
fcs[None] = [0, bs2none, none2bs]
fcs[False] = [1, bs2false, false2bs]
fcs[True] = [2, bs2true, true2bs]
fcs[int] = [3, bs2int, int2bs]
fcs[float] = [4, bs2float, float2bs]
fcs[bytes] = [5, bs2bytes, bytes2bs]
fcs[str] = [6, bs2str, str2bs]
fcs[list] = [7, bs2list, list2bs]
fcs[tuple] = [8, bs2tuple, tuple2bs]
fcs[dict] = [9, bs2dict, dict2bs]
t2bs = {}
i2t = {}
for k,v in fcs.items():
    bs = bytes([v[0]])
    t2bs[k] = bs
    i2t[v[0]] = k
def _bs2val(bs):
    tp = i2t[bs[0]]
    fc = fcs[tp][1]
    return fc(bs)
def val2bs(val):
    #print(f"[DEBUG.str] val2bs: {type(val)}")
    tp = type(val)
    if tp not in fcs and val in {None, False, True}:
        tp = val
    fc = fcs[tp][2]
    rst = fc(val)
    #print(f"[DEBUG.str] done val2bs: {len(rst)}")
    return rst
def bs2val(bs):
    #print(f"[DEBUG.str] bs2val: {len(bs)}")
    if bs is None or len(bs)==0:
        return bs
    rst = _bs2val(bs)[0]
    #print(f"[DEBUG.str] done bs2val: {type(rst)}")
    return rst


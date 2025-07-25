from buildz import pyz
from ..base import Args
def isdict(obj):
    return type(obj)==dict
def islist(obj):
    return type(obj) in (list, tuple)
def tolist(obj):
    if not islist(obj):
        obj = [obj]
    return obj
def dict2list(obj):
    if type(obj)!=dict:
        return obj
    return list(obj.items())
def dict2iter(obj):
    if type(obj)!=dict:
        return obj
    return obj.items()
def get(obj, key, default=None, set = False):
    if type(obj)==list:
        key = int(key)
        if len(obj)<=key:
            return default
        return obj[key]
    else:
        if key not in obj:
            if set:
                obj[key] = default
            return default
        return obj[key]

pass
def getf(obj, key, fc):
    if key not in obj:
        return fc()
    return obj[key]

pass
def gfn(obj, **maps):
    rst = []
    for k in maps:
        if k in obj and obj[k] is not None:
            v = obj[k]
        else:
            v = maps[k]()
        rst.append(v)
    if len(rst)==1:
        rst = rst[0]
    return rst

pass
def gf(obj, **maps):
    rst = []
    for k in maps:
        if k in obj:
            v = obj[k]
        else:
            v = maps[k]()
        rst.append(v)
    if len(rst)==1:
        rst = rst[0]
    return rst

pass
def get_first(obj, keys, default = None):
    for k in keys:
        if k in obj:
            return obj[k],1
    return default,0

pass
def get_one(obj, keys, default=None):
    return get_first(obj, keys, default)[0]
def g1(obj, **maps):
    v = None
    for k in maps:
        v = maps[k]
        if k in obj:
            v = obj[k]
            return v
    return v

pass
def g(obj, **maps):
    rst = []
    if obj is None:
        return maps.values()
    for k in maps:
        v = maps[k]
        if k in obj:
            v = obj[k]
        rst.append(v)
    if len(rst)==1:
        rst = rst[0]
    return rst

pass
def c(obj, **maps):
    for k in maps:
        v = maps[k]
        if k not in obj:
            return False
        vo = obj[k]
        if vo!=v:
            return False
    return True
def gs(obj, **maps):
    rst = []
    for k in maps:
        v = maps[k]
        if k in obj:
            v = obj[k]
        else:
            obj[k] = v
        rst.append(v)
    if len(rst)==1:
        rst = rst[0]
    return rst

pass
def get_set(obj, key, val):
    if key not in obj:
        obj[key]=val
    return obj[key]
def s(obj, **maps):
    for k in maps:
        v = maps[k]
        obj[k] = v

pass
def fill_fc(maps, fc):
    for k in maps:
        v = maps[k]
        if type(v) == dict:
            fill_fc(v, fc)
            continue
        maps[k] = fc(v)
    return maps

pass
def im2l(maps):
    if type(maps)!=dict:
        return maps
    mx = 0
    for k in maps:
        if type(k)==str:
            k = int(k)
        if type(k)!=int or k<0:
            raise Exception(f"args key only can be int and bigger than 0, but {type(k)}:{k} found")
        mx = max(k+1, mx)
    arr = [None]*mx
    for k, v in maps.items():
        arr[k] = v
    return arr

pass
    
def dset(maps, keys, val):
    if type(keys) not in (list,tuple):
        keys = [keys]
    for key in keys[:-1]:
        if type(maps)==dict:
            if key not in maps:
                maps[key] = {}
        else:
            key = int(key)
        maps = maps[key]
    maps[keys[-1]] = val

pass
def dhas(maps, keys):
    if type(keys) not in (list,tuple):
        keys = [keys]
    for key in keys:
        if type(maps)==dict:
            if key not in maps:
                return False
        else:
            key = int(key)
            if key>=len(maps):
                return default
        maps = maps[key]
    return True

pass

def keys(key, spt='.', code='utf-8'):
    if type(key) not in (list, tuple):
        if type(key)==bytes:
            key = key.decode(code)
        if type(key)!=str:
            key = str(key)
        key = key.split(spt)
    return key
def dget(maps, keys, default = None):
    if type(keys) not in (list,tuple):
        keys = [keys]
    for key in keys:
        find = 1
        if type(maps)==dict:
            find = key in maps
        elif type(maps) in (list, tuple):
            try:
                key = int(key)
            except:
                key = len(maps)
            find = key<len(maps)
        else:
            find = False
        if not find:
            return default,0
        maps = maps[key]
    return maps,1

pass
def dmatch(maps, keys, fc_map = lambda x:x):
    if type(keys) not in (list,tuple):
        keys = [keys]
    deep=0
    src = maps
    for key in keys:
        find = 1
        maps = fc_map(maps)
        if type(maps)==dict:
            find = key in maps
        elif type(maps) in (list, tuple):
            try:
                key = int(key)
            except:
                key = len(maps)
            find = key<len(maps)
        else:
            find = False
        if not find:
            break
        deep+=1
        src = maps[key]
    return src,deep

def dremove(maps, keys):
    if type(keys) not in (list,tuple):
        keys = [keys]
    arr = []
    for key in keys:
        if key not in maps:
            break
        arr.append([maps, key])
        maps = maps[key]
    arr.reverse()
    first=1
    for maps,key in arr:
        if first or len(maps[key])==0:
            del maps[key]
        first=0
    return

pass

def dhget(maps, keys):
    if type(keys) not in (list,tuple):
        keys = [keys]
    for key in keys:
        find = 1
        if type(maps)==dict:
            find = key in maps
        elif type(maps) in (list, tuple):
            try:
                key = int(key)
            except:
                key = len(maps)
            find = key<len(maps)
        else:
            find = False
        if not find:
            return None, find
        maps = maps[key]
    return maps, True

pass
def l2m(arr, **maps):
    rst = {}
    i = 0
    for k in maps:
        if i<len(arr):
            val = arr[i]
        else:
            val = maps[k]
        rst[k] = val
        i+=1
    return rst

pass
def deep_fill_argx(src, target, replace=1):
    # print(f"src:{src}")
    # print(f"target:{target}")
    if not isinstance(src, Args):
        if type(src) in (list, tuple):
            src = Args(src)
        elif type(src)==dict:
            src = Args([], src)
        else:
            return
    tp = type(target)
    if not isinstance(target, Args):
        if tp == list:
            target = Args(target)
        elif tp == dict:
            target = Args([], target)
        else:
            return
    for it in src.lists:
        target.args.append(it)
    for k,v in src.dicts.items():
        if k not in target.dicts:
            target.dicts[k] = v
            continue
        tv = target.dicts[k]
        if Args.is_collect(tv) and Args.is_collect(v):
            deep_fill_argx(v, tv, replace)
        elif replace:
            #print(f"[TESTZ] replace: {k}:{tv} to {v}")
            target.dicts[k] = v



def deep_update(target, src, replace=1):
    """
        dict深层更新，src[key]是dict就深入更新，否则:
            src有而target没有就替换，否则：
                replace=1就替换
    """
    for k in src:
        val = src[k]
        if k not in target:
            target[k] = val
            continue
        mval = target[k]
        if type(mval) == dict and type(val)==dict:
            deep_update(mval, val, replace)
        else:
            if replace:
                target[k] = val

pass
update = deep_update
def deep_fill(src, target, replace=1):
    return deep_update(target, src, replace)

pass
def deep_clone(obj):
    if type(obj)==list:
        rst = []
        for it in obj:
            rst.append(deep_clone(it))
    elif type(obj)==dict:
        rst = {}
        for k,v in obj.items():
            rst[k] = deep_clone(v)
    else:
        rst = obj
    return rst
pass
fill=deep_fill

def maps(**kv):
    return kv

pass

def flush_maps(maps, fc_key = lambda x:x.split(".") if type(x)==str else [x], visit_list=False):
    if type(maps)==list:
        if not visit_list:
            return maps
        rst = [flush_maps(it, fc_key, visit_list) for it in maps]
        return rst
    if type(maps)!=dict:
        return maps
    rst = {}
    for k,v in maps.items():
        ks = fc_key(k)
        v = flush_maps(v, fc_key, visit_list)
        dset(rst, ks, v)
    return rst

pass
def unflush_maps_item(rst, keys, val, fc_key):
    if type(val)!=dict:
        key = fc_key(keys)
        rst[key] = val
        return
    for k, v in val.items():
        unflush_maps_item(rst, keys+[k], v, fc_key)
def unflush_maps(maps, fc_key = lambda x:".".join([str(k) for k in x]) if type(x) in (list, tuple) else str(x)):
    if type(maps)!=dict:
        return maps
    rst = {}
    for k,v in maps.items():
        unflush_maps_item(rst, [k], v, fc_key)
    return rst

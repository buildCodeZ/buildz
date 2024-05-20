
def get(obj, key, default=None, set = False):
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
def get_first(obj, *keys):
    for k in keys:
        if k in obj:
            return obj[k]
    raise KeyError(keys[0])

pass
def get_one(obj, keys, default = None):
    for k in keys:
        if k in obj:
            return obj[k]
    return default

pass
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
    for k in maps:
        v = maps[k]
        if k in obj:
            v = obj[k]
        rst.append(v)
    if len(rst)==1:
        rst = rst[0]
    return rst

pass
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
def s(obj, **maps):
    for k in maps:
        v = maps[k]
        obj[k] = v

pass
def sets(maps, keys, val):
    if type(keys) != list:
        keys = [keys]
    for key in keys[:-1]:
        if key not in maps:
            maps[key] = {}
        maps = maps[key]
    maps[keys[-1]] = val

pass
def gets(maps, keys, default = None):
    if type(keys) != list:
        keys = [keys]
    for key in keys:
        if key not in maps:
            return default
        maps = maps[key]
    return maps

pass
def removes(maps, keys):
    if type(keys) != list:
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
    return None

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

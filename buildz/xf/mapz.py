
def get(obj, key, default=None):
    if key not in obj:
        return default
    return obj[key]

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
            src有而maps没有就替换，否则：
                replace=1就替换
    """
    for k in src:
        val = src[k]
        if k not in target:
            target[k] = val
            continue
        mval = target[k]
        if type(mval) == dict and type(val)==dict:
            update_maps(mval, val, replace)
        else:
            if replace:
                target[k] = val

pass
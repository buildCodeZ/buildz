
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

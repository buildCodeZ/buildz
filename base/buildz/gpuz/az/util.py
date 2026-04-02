

def mul(arr):
    if type(arr) not in {list, tuple}:
        return arr
    i=1
    for j in arr:
        i*=j
    return i

def exp(val, dims):
    if val is None:
        return None
    if type(val) not in {list, tuple}:
        val = [val]*dims
    return val

def format_size(n):
    unit = ",K,M,G,T".split(",")
    i=0
    while n>=1024 and i<len(unit)-1:
        n = n/1024
        i+=1
    n = "%.3f"%(n,)
    return f"{n}{unit[i]}"

def nsize(fmt):
    fmt=fmt.strip()
    unit = ",K,M,G,T".split(",")
    maps = {}
    val=1
    for k in unit:
        maps[k] = val
        val =val*1024
    k= fmt[-1]
    if k not in maps:
        k = ""
    val = float(fmt[:len(fmt)-len(k)])
    return val*maps[k]

pass
ns=nsize

fmt_sz = format_size
fmt_size=format_size
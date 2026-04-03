

def mul(arr):
    from collections.abc import Iterable
    if not isinstance(arr, Iterable):
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

def format_size(n, unit=1024):
    units = ",K,M,G,T,P,E,Z,Y".split(",")
    i=0
    while n>=unit and i<len(units)-1:
        n = n/unit
        i+=1
    n = "%.3f"%(n,)
    return f"{n}{units[i]}"

def nsize(fmt, unit=1024):
    fmt=fmt.strip()
    units = ",K,M,G,T,P,E,Z,Y".split(",")
    maps = {}
    val=1
    for k in units:
        maps[k] = val
        val =val*unit
    k= fmt[-1]
    if k not in maps:
        k = ""
    val = float(fmt[:len(fmt)-len(k)])
    return val*maps[k]

pass
ns=nsize

fmt_sz = format_size
fmt_size=format_size
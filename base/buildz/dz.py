
from ._dz.mapz import *
from ._dz.str import *
from ._dz.omapz import Mapz
from ._dz.conf import Conf, BindKey
from ._dz.confx import Conf as Confx
from ._dz.oconf import ObjConf, ObjTypeConf
from ._dz.check import Check
def format_size(n, unit=1024):
    units = ",K,M,G,T,P,E,Z,Y".split(",")
    i=0
    while n>=unit and i<len(units)-1:
        n = n/unit
        i+=1
    n = "%.3f"%(n,)
    return f"{n}{units[i]}"

def nsize(fmt, unit=1024):
    if type(fmt)!=str:
        return fmt
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

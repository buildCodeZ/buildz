#

from buildz.argzx import conf_argz as argzx
from buildz.tls import *
conf = xf.loads(r"""
#range=(0,12,3)
range=(0,12,3)
args: {
    0:[0,0]
}
maps: {
    a={
        src: [(1,list)]
    }
}
""")
def test():
    args = [0,1,2]
    maps = {'a':'b','c':'d'}
    bd = argzx.FullArgsBuild()
    obj = bd(conf)
    args, maps = obj(args, maps)
    print(f"obj: {obj}")
    print(f"args: {args}, maps: {maps}")
    pass

pass

pyz.lc(locals(),test)
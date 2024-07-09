#python
"""
测试代码
测试xf.loads和json.loads的速度
在修改json的scanner.py(不让它用c_make_scanner这个底层优化函数)
耗时对比如下：

json
time cost in <function loads at 0x0000015DEDD0D9E0>: 0.04396796226501465

xf
time cost in <function loads at 0x0000015DEDD0F100>: 0.3307473659515381

慢7倍多，感觉还能接受，之前没注意速度，更早的版本(buildz.xf.read.loads，后面可能会删掉)耗时要三四秒，对比之后就重新写了个，也不管什么堆栈了，就递归调用，后面有时间再改回堆栈吧（python的list的append和pop效率貌似不咋地，尤其是pop(0)）
又写了个C版本的代码来加速，速度大概比C加速版json的慢三到四倍（汗，和没用C加速版的json差不多速度，追求结构化不追求速度，用C只是因为C本身比python快，起码满足自己使用了，本测试代码里C加速版xf比python版快7倍，在其他场景里实际使用快了近一百倍），源码暂不公布（C语言要自己写垃圾回收真累，还要自己写List和Map，另外就是用C写了后，发现除了当库给其他语言使用，貌似没啥用）
"""
from buildz.xf import readz as rz
from buildz.xf import read as rd
from buildz import xf, fz
import json
import time

try:
    # C加速代码
    import cxf
except:
    from buildz.xf import read as cxf
    pass
pass
def cost(n, f,*a,**b):
    c = time.time()
    r = f(*a,**b)
    d = time.time()-c
    print(f"time cost in {n}-{f}: {d}")
    return r, d

pass

n = 100
m = 13
l = 12
_arr = [123]
print("test A")
for i in range(n):
    _arr = [list(_arr)]

pass
print("test B")
_map = {}
for i in range(m):
    _map[i] = dict(_map)

pass
print("test C")
rst = []
for i in range(l):
    rst.append([_arr,_map])

pass
print("test D")
json.dumps(_arr)
print("test E")
json.dumps(_map)
print("test F")
js = json.dumps(rst)
#js = fz.read(fp, 'r')
#js = "\n\n"+js+"\n"
#js = xf.dumps(rst, json_format=1)
# js = r"""
# [
#     1,2,3,{"4":5,"6":7,"8":9,"10":11,"4":6}
# ]
# """
print("start")
num = 10
cs = [0,0,0]
for i in range(num):
    jv,cj = cost("json.loads", json.loads,js)
    xv,cx = cost("rz.loads",rz.loads,js)
    cv,cv = cost("cxf.loads", cxf.loads, js)
    cs[0]+=cj
    cs[1]+=cx
    cs[2]+=cv
print(f"judge: {jv==xv}")
print(f"judge: {jv==cv}")
print(f"json mean cost: {cs[0]/num}")
print(f"xf mean cost: {cs[1]/num}")
print(f"cxf mean cost: {cs[2]/num}")
print(f"xf cost =  {'%.3f'%(cs[1]/cs[0],)} json")
print(f"cxf cost = {'%.3f'%(cs[2]/cs[0],)} json")
print(f"xf cost = {'%.3f'%(cs[1]/cs[2],)} cxf")
#_xv = cost("rd.loads",rd.loads, js)
#with open("test.json", 'w') as f:
#    f.write(js)
if n>3 or m>3 or l > 3:
    exit()
print(json.dumps(jv))
print(json.dumps(xv))




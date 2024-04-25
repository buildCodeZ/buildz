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
"""
from buildz.xf import readz as rz
from buildz.xf import read as rd
from buildz import xf
import json
import time

def cost(n, f,*a,**b):
    c = time.time()
    r = f(*a,**b)
    d = time.time()-c
    print(f"time cost in {n}-{f}: {d}")
    return r

pass

n = 100
m = 12
l = 11
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
js = "\n\n"+js+"\n"
#js = xf.dumps(rst, json_format=1)
# js = r"""
# [
#     1,2,3,{"4":5,"6":7,"8":9,"10":11,"4":6}
# ]
# """
print("start")
jv = cost("json.loads", json.loads,js)
xv = cost("rz.loads",rz.loads,js)
print(f"judge: {jv==xv}")
_xv = cost("rd.loads",rd.loads, js)
#with open("test.json", 'w') as f:
#    f.write(js)
if n>3 or m>3 or l > 3:
    exit()
print(json.dumps(jv))
print(json.dumps(xv))




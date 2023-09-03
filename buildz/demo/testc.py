#coding=utf-8

from buildz import xconfz as xf
print(xf.__path__)
s = "{a:}"
arr = [
    "[]",
    "{a:'',b:''}",
    "{a:''}",
    "{'':''}",
    "{a:'',b:''}"
]

for a in arr:
    print("data:", a)
    xf.loads(a)

pass

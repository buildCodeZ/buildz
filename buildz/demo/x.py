from buildz import xconfz as xf

print(xf.loads("{a:<1,i>}"))

p = print
p(xf.dumps([]))
d=xf.dumps
pd = lambda x:p(d(x))

pd({})
pd([''])


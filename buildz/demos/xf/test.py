from buildz import xf

from os.path import join, dirname
dp = dirname(__file__)
fp = join(dp, "test.js")

s = xf.fread(fp)
obj = xf.loads(s)

rs = xf.dumps(obj, format=1, deep = 1)
print(rs)
args = xf.args()
print("args from cmd:", args)

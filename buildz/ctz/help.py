#
from os.path import dirname, join
dp = dirname(__file__)
fp = join(dp, "readme.md")
with open(fp, 'rb') as f:
    s = f.read().decode("utf-8")
print(s)
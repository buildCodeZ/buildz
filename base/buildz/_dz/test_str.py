
from buildz import dz
import json
import base64
obj = {'list': [1,2,3,4567], 'tuple': ('a', 'b', 'c'), None:False, True:{0:1,2:3,4:5.6}, 'bytes': b'asfdjiojzoicxv0x00', 'str':'测试中文'}
bs = dz.val2bs(obj)
val = dz.bs2val(bs)
print(f"bs: {bs, len(bs)}")
obj['bytes'] = base64.b64encode(obj['bytes']).decode()
js = json.dumps(obj)
print(f"js: {js, len(js)}")
js = json.dumps(obj, ensure_ascii=False)
print(f"js: {js, len(js)}")

print(f"val: {val}")

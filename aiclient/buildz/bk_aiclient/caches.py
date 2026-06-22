
import hashlib
__doc__="""
从文件/页面读取的数据的缓存，主要是为了分片读取的时候可以不用重复读取文件/页面
不过小模型在调用工具的时候基本不管这些参数
"""
class Caches:
    def __init__(self, size=100, key_size=64):
        self.caches = {}
        # [[offset, key, val], ...]
        self.datas = [None]*size
        self.key_size = key_size
        self.count=0
    def get_index(self):
        find, mn, key = None, None, None
        for i in range(len(self.datas)):
            data = self.datas[i]
            if data is None:
                find = i
                break
            if mn is None or data[0]<mn:
                find = i
                mn = data[0]
                key = data[1]
        return find, key
    def sub(self, prefix):
        def fc(key, fc, base=0, last=-1, reuse=True):
            key = prefix+key
            return self.get(key, fc, base, last, reuse)
        return fc
    def get(self, key, fc, base=0, last=-1, reuse=True):
        if len(key)>self.key_size:
            key = hashlib.md5(key.encode("utf-8")).hexdigest()
        if key in self.caches and reuse:
            data = self.datas[self.caches[key]]
            data[0] = self.count
            self.count+=1
            data = data[2]
        else:
            data = fc()
            index, old_key = self.get_index()
            if old_key in self.caches:
                del self.caches[old_key]
            self.caches[key] = index
            self.datas[index] = [self.count, key, data]
            self.count+=1
        if last<0:
            last = len(data)
        return data[base:last]

pass
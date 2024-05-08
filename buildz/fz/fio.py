#coding=utf-8

"""
读写文件再简化
"""
def fread(fp, mode='rb'):
    with open(fp, mode) as f:
        return f.read()

pass
read=fread
def freads(fp, mode = 'rb', size=1024*1024):
    with open(fp, mode) as f:
        while True:
            bs = f.read(size)
            if len(bs)==0:
                break
            yield bs

pass
reads=freads

def fwrite(ct, fp, mode = 'wb'):
    with open(fp, mode) as f:
        f.write(ct)

pass
write = fwrite
def fwrites(cts, fp, mode = 'wb'):
    with open(fp, mode) as f:
        for ct in cts:
            f.write(ct)

pass
writes = fwrites
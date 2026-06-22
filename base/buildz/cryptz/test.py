from buildz import cryptz
from buildz.tz import time as timez
import hashlib
tm = timez.Timer()
cpt = cryptz.ByteStream(b"test")
cpt = cryptz.BlockCrypt(b"test")
bs = b'1'*1024*1024*40
tm()
outs = cpt.encrypt(bs)
sec = tm()
print(f"time cost for {len(bs), len(outs)}: {sec}")
exit()
cp = cpt.encryptor
tm()
outs = b""
n=len(bs)
#n=1024*10
#n=32
cds = b''
mids = b''
#nxt = hashlib.md5(data).hexdigest().encode("ascii")
for i in range(0, len(bs), n):
    nxt = hashlib.md5(cds).hexdigest().encode("ascii")
    mids+=nxt
    cds=nxt
    outs += cp.update(bs[i:i+n])
sec=tm()
print(f"time cost for {len(bs), len(outs), len(mids)}: {sec}")


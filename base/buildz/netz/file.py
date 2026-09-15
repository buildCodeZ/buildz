
import socket
from buildz import xf,dz,fz,args as argx, log as logz
from .tcp.base import *
from .tcp.blkskt import BlockSocket
s="""
(order,addr,file,tfile)
{   
    a:addr
    f:file
    t:tfile
}
"""
fetch = argx.Fetch(*xf.loads(s))
conf=fetch()
log=logz.simple("./bz_nf.log")
od,addr,fp,tfp=dz.g(conf, order="s",addr="0.0.0.0:9876",file=None,tfile=None)
#log.info(f"od: {od}, {type(od)}")
od = od.lower()[:1]
assert len(od)>0 and od in {'s','c'}, f'order should be s/server/c/client'
addr = fetch_addr(addr)
skt=new_skt(addr)
try:
    if od=='s':
        skt.bind(addr)
        skt.listen(10)
        while True:
            try:
                cli,addr=skt.accept()
                cli=BlockSocket.wrap(cli)
                fp = cli.recv().decode("utf-8")
                bs = cli.recv()
                fz.write(bs,fp)
                cli.close()
                log.info(f"done recv: {fp}, {len(bs)} bytes")
            except Exception as exp:
                log.error(f"exp: {exp}")
    elif od=='c':
        assert fp is not None
        tfp = tfp or fp
        skt.connect(addr)
        skt=BlockSocket.wrap(skt)
        bs = fz.read(fp)
        skt.send(tfp.encode("utf-8"))
        skt.send(bs)
        log.info(f"done send: {fp} to {tfp}: {len(bs)} bytes")
finally:
    skt.close()

pass

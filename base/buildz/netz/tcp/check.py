
import socket
import sys
from buildz import xf, fz, dz, args as argx, log as logz

fetch = argx.Fetch(*xf.loads(r"""
(addr),
{
    h:host
    host:ip
    p:port
}
"""))

conf = fetch()
addr, ip, port = dz.g(conf, addr=None,ip=None,port=None)

if addr is not None:
    arr = addr.split(":")
    ip = arr[0]
    if len(arr)>1:
        port=int(arr[1])

pass
addr = (ip, port)
skt=socket.socket()
try:
    skt.connect(addr)
    print(f"{addr} is connectable")
except Exception as exp:
    print(f"exp: {exp}")
    print(f"{addr} not connectable")
finally:
    skt.close()

pass




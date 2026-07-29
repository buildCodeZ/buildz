import os
from buildz.netz.tcp import midserver as ms
from buildz.netz import sc
from getpass import getpass
from buildz.netz.sslz import cert as certz
from buildz import args as argx, xf, dz, log as logz, fz
fetch = argx.Fetch(*xf.loads(r"""
(action, addr, localaddr, remoteaddr, listen),
{
    la: localaddr
    ra: remoteaddr
    l:la
    r:ra
    a: addr
    c: cert
    p: prv
    pk: prv_key
    pwd: password
    ca: cas
    conf: confpath
    log: logpath
    // sid
}
(listen)
"""))
def test():
    conf = fetch()
    fp = conf.get("confpath", None)
    if os.path.isfile(fp):
        src = xf.loadf(fp).get("conf", {})
        dz.fill(src, conf, replace=0)
    act, addr, laddr, raddr, listen, log = dz.g(conf, action=0, addr=0, localaddr=0, remoteaddr=0, listen=0, logpath="log.txt")
    log = logz.simple(log)("test")
    log.debug(f"conf: {conf}")
    cert, prv, pwd, cas, sid = dz.g(conf, cert=None, prv=False, password=None, cas=None, sid=None)
    if cas:
        if type(cas)!=list:
            cas = cas.split(",")
        rst = []
        for fp in cas:
            rst+=certz.loadf_certs(os.path.expanduser(fp))
        cas = rst
    prv_key = None
    cert = os.path.expanduser(cert)
    cert = fz.read(cert)
    if prv:
        prv = os.path.expanduser(prv)
        try:
            prv = certz.loadf_prv(prv, pwd)
        except:
            pwd = getpass(f"input password for {prv}:")
            prv = certz.loadf_prv(prv, pwd)
    deal_fc = sc.Verify(cert, prv, sid, cas)
    act = act.lower()[0]
    if act=='s':
        sv = ms.MidServer(addr, log=log, deal_fc = deal_fc)
        sv()
    elif act == 'c':
        cl = ms.MidClient(addr, log=log, deal_fc= deal_fc)
        cl.connect(laddr, raddr, listen)
        cl()
    else:
        assert 0

pass

if __name__=="__main__":
    test()
pass

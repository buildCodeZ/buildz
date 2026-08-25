import os,time
from buildz.netz.tcp import midserver as ms
from buildz.netz import sc
from getpass import getpass
from buildz.netz.sslz import cert as certz
from buildz import args as argx, xf, dz, log as logz, fz, pyz
fetch = argx.Fetch(*xf.loads(r"""
(action, addr, localaddr, remoteaddr, listen),
{
    la: localaddr
    ra: remoteaddr
    a: addr
    c: cert
    p: prv
    pk: prv_key
    pwd: password
    ca: cas
    conf: confpath
    log: logpath
    l: listen
    d: debug
    o:opens
    opens:open_ports
    r4c: restart_for_close
    r4x: restart_for_except
    // sid
}
(listen,l,d,debug, r4c, r4x)
"""))
def deal_ports(ports):
    if ports is None:
        return None
    if type(ports)==set:
        ports = list(ports)
    if type(ports) not in (list,tuple):
        ports = [ports]
    rst = []
    for port in ports:
        if type(port)==int:
            rst.append(port)
            continue
        arr = port.split(",")
        for tmp in arr:
            tmp=tmp.strip()
            if tmp.find("-")<0:
                tmp = int(tmp)
                rst.append(tmp)
                continue
            down,up=tmp.split("-")
            up = int(up.strip())
            down=int(down.strip())
            rst+=list(range(down, up+1))
    return set(rst)
def test():
    conf = fetch()
    fp = conf.get("confpath", None)
    if os.path.isfile(fp):
        src = xf.loadf(fp).get("conf", {})
        dz.fill(src, conf, replace=0)
    act, addr, laddr, raddr, listen, log,debug = dz.g(conf, action=0, addr=0, localaddr=0, remoteaddr=0, listen=0, logpath="log.txt",debug=0)
    act = act.lower()[0]
    def_r4c = False if act=='s' else True
    restart4exp,restart4close = dz.g(conf, restart_for_except=True, restart_for_close=def_r4c)
    shows = 'info,warn,error'.split(",")
    if debug:
        shows.append("debug")
    log = logz.simple(log,shows=shows)("test")
    log.debug(f"conf: {conf}")
    log.info(f"restart4exp: {restart4exp}, restart4close: {restart4close}")
    cert, prv, pwd, cas, sid = dz.g(conf, cert=None, prv=False, password=None, cas=None, sid=None)
    open_ports = dz.g(conf, open_ports=None)
    open_ports=deal_ports(open_ports)
    log.info(f"open_ports: {type(open_ports), len(open_ports) if open_ports is not None else None}")
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
    deal_fc = sc.Verify(cert, prv, sid, cas, do_yield=True)
    while True:
        try:
            if act=='s':
                # deal_fc = sc.Verify(cert, prv, sid, cas, do_yield=True)
                sv = ms.MidServer(addr, log=log, deal_fc = deal_fc, open_ports=open_ports)
                sv()
            elif act == 'c':
                cl = ms.MidClient(addr, log=log, deal_fc= deal_fc)
                cl.connect(laddr, raddr, listen)
                cl()
            else:
                assert 0
        except Exception as exp:
            log.error(f"exp in midsv: {exp}")
            log.error(f"full exp: {pyz.s_exp()}")
            if not restart4exp:
                break
            log.info(f"restart for exception: {exp}")
            time.sleep(5.0)
            continue
        if restart4close:
            time.sleep(5.0)
            continue
        break

pass

if __name__=="__main__":
    test()
pass

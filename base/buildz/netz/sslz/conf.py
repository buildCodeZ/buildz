
from . import cert as certz, pk as pkz
from buildz import xf, fz, dz, args as argz, log as logz
from getpass import getpass

conf = xf.loads("""
(call, outfp)
{
    o: outfp
    p: pwd
    prv: private_key
    P: need_pwd
    common: params.common
    uid: params.userID
    country: params.country
    before: params.valid_before
    after: valid
    valid: params.valid
    l:log
}
(P, need_pwd)
""")

fetch = argz.Fetch(*conf)

calls = {}
def test():
    conf = fetch()
    conf = xf.flush_maps(conf)
    log_fp =conf.get("log", "buildz_sslz.log")
    log = logz.simple(log_fp)
    call = conf.get("call")
    ofp = conf.get("outfp")
    need_pwd = conf.get("need_pwd", False)
    pwd = conf.get("pwd", None)
    fp_prv = conf.get("private_key")
    fconf = conf.get("conf")
    params = {}
    if fconf:
        params = xf.loadf(fconf)
    args = conf.get("param", {})
    dz.deep_fill(args, params)
    log.debug(f"call: '{call}', conf: {conf}")
    if need_pwd and pwd is None:
        pwd = getpass("input password:")
    if call == 'prv':
        certz.genf_prv(ofp, pwd)
    elif call == 'pub':
        assert fp_prv is not None
        certz.genf_pub(ofp, fp_prv, pwd)
    elif call == 'cert':
        assert fp_prv is not None
        certz.genf_root_cert(ofp, certz.loadf_prv(fp_prv, pwd), conf=params)
    elif call == 'csr':
        assert fp_prv is not None
        certz.genf_csr(ofp, certz.loadf_prv(fp_prv, pwd), conf=params)
    elif call == 'sign':
        fp_csr = conf.get("csr")
        fp_cert = conf.get("cert")
        assert fp_prv is not None
        assert fp_csr is not None
        assert fp_cert is not None
        certz.signf_csr(ofp, certz.loadf_prv(fp_prv, pwd), certz.loadf_csr(fp_csr), certz.loadf_cert(fp_cert)) 
    elif call in ('show_csr', 'show_cert'):
        if call == 'show_csr':
            subject = certz.loadf_csr(ofp).subject
        elif call == 'show_cert':
            subject = certz.loadf_cert(ofp).subject
        rst = certz.des_subject(subject)
        rs = xf.dumps(rst, format=1)
        print(f"{call} {ofp}:\n{rs}")
    elif call in ('verify_csr', "verify_cert", "verify_certs"):
        if call == 'verify_csr':
            rst = certz.verifyf_csr(ofp)
        elif call == 'verify_cert':
            rst = certz.verifyf_cert(ofp)
        elif call == 'verify_certs':
            cas = conf.get("cas", [])
            cas = [certz.loadf_cert(ca) for ca in cas]
            rst = certz.verifyf_certs(ofp, cas)
        print(f"{call} {ofp}: {rst}")

    
if __name__=="__main__":
    test()
'''
gen prv fp -p ...
gen pub -o pub.pk --prv prv.pk -p ...
gen cert root.cert --param.common --conf cert.conf --prv prv.pk
gen csr lx.csr --conf csr.conf --prv prv.pk
gen sign lx.cert --cert root.cert --prv root.prv
'''

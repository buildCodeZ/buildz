from .dz import Conf
from . import xf, pathz, pyz, argx
import sys, os
def load_conf(conf, dp=None, dp_key = 'dp', src_key = 'src.conf'):
    if type(conf)==dict:
        conf = Conf().update(conf)
    fps, base = conf.gets('fps, conf', [], {})
    if type(fps)==str:
        fps = [fps]
    conf_first,replace,flush,visit_list = conf.gets('conf_first,replace,flush,visit_list',1, 1,1,0)
    spt, spts = conf.gets('spt, spts','.',',')
    dp = conf.get(dp_key, dp)
    path = pathz.Path()
    path.set("dp", dp)
    rst = Conf(spt, spts)
    if src_key is not None:
        rst.set(src_key, conf)
    if conf_first:
        rst.update(base, flush, replace, visit_list)
    for fp in fps:
        tmp = xf.loadf(path.dp(fp))
        rst.update(tmp, flush, replace, visit_list)
    if not conf_first:
        rst.update(base, flush, replace, visit_list)
    return rst
# using
def calls(conf):
    calls = conf.get("calls", [])
    if type(calls)==str:
        calls = [calls]
    for key in calls:
        assert conf.has(key), f"not has key: '{key}'"
        simple(conf(key))
def simple(conf):
    fc = conf.get('fc')
    if fc is None:
        fc = calls
    else:
        #assert fc is not None
        fc = pyz.load(fc)
    return fc(conf)
def get_sys_conf(conf = []):
    if type(conf) == str:
        conf = xf.loadf(conf)
    if conf is None:
        conf = []
    fetch = argx.Fetch(*conf)
    return fetch()
def run(dp = None, fp = None, init_conf = {}):
    if dp is None:
        dp = os.path.dirname(__file__)
    path = pathz.Path()
    path.set('dp', dp)
    conf = {}
    if fp is not None:
        conf = xf.loadf(path.dp(fp))
    #sys_conf = get_sys_conf()
    xf.fill(init_conf, conf, 1)
    conf = Conf().update(conf)
    init = conf.get(conf.get("key.init", "init"), {})
    conf = load_conf(conf, dp).update(init)
    simple(conf)
def test():
    run()
pyz.lc(locals(), test)
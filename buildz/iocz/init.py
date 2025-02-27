#

from .conf import mg
from .. import xf
s_default_conf = r"""
confs.pri: {
    deal_obj:{
        type=deal
        src=<buildz>.iocz.conf_deal.obj.ObjectDeal
        deals: [obj,object]
        call=1
    }
    deal_val:{
        type=deal
        src=<buildz>.iocz.conf_deal.val.ValDeal
        deals: [val,value]
        call=1
    }
    deal_ref: {
        type:deal
        src:<buildz>.iocz.conf_deal.ref.RefDeal
        deals: ref
        call=1
    }
    deal_ioc: {
        type:deal
        src:<buildz>.iocz.conf_deal.ioc.IOCDeal
        deals: ioc
        call=1
    }
}
builds: [deal_obj,deal_val,deal_ref,deal_ioc]
""".replace("<buildz>", "buildz")
def build(conf = None, default_conf = True):
    global s_default_conf
    if default_conf and type(default_conf) not in (str, list, tuple, dict):
        default_conf = s_default_conf
    if type(default_conf) == str:
        default_conf = xf.loads(default_conf)
    obj = mg.ConfManager(conf)
    if default_conf:
        obj.add_conf(default_conf)
    return obj

pass
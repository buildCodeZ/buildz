from ..iocz.conf import conf
from .. import Base, xf, dz,pyz
from .callz import *
from ..iocz.ioc_deal.base import BaseEncape,BaseDeal
from ..iocz.conf.up import BaseConf
from .conf_argz import *
from .evalx import *
from .. import iocz
from . import argz
class EnvFc(Fc):
    def init(self, unit):
        super().init()
        self.unit = unit
    def call(self, params):
        self.unit.update_env(params.maps)
        return True,1
class ArgsCallEncape(BaseEncape):
    def init(self, fcs, args, eval, unit):
        super().init()
        self.fcs = fcs
        self.args = args
        self.eval = eval
        self.call_fc = None
        self.unit = unit
    def ref(self, key, unit):
        key = self.obj(key)
        if type(key)==str:
            rst, find = unit.get(key)
            assert find, f"fc not found: '{key}'"
            key=rst
        return key
    def call(self, params=None):
        if self.call_fc is None:
            fcs = [self.ref(fc, self.unit) for fc in self.fcs]
            self.call_fc = Call(fcs, self.args, self.eval)
        return self.call_fc
class ArgsCallDeal(BaseDeal):
    def init(self, fc=True, update_env = False):
        super().init()
        _conf = BaseConf()
        index=1
        self.fc = fc
        self.update_env = update_env
        if fc:
            _conf.ikey(1, 'fc', 'fcs,calls,call'.split(','))
            _conf.ikey(2, 'eval', "judges,judge,evals".split(","))
            _conf.ikey(3, 'conf')
        else:
            _conf.ikey(2, 'eval', "judges,judge,evals".split(","))
            _conf.ikey(1, 'conf')
        self.update=_conf
        self.args_builder = FullArgsBuilder()
    def deal(self, conf, unit):
        conf_eval = dz.g(conf, eval=None)
        conf_args = dz.g(conf, conf=None)
        _eval = None
        if conf_eval is not None:
            _eval = evalBuilder(conf_eval)
        _args = None
        if conf_args is not None:
            _args = self.args_builder(conf_args)
        if self.fc:
            fcs = dz.g(conf, fc=[])
            if type(fcs)==str:
                fcs = [fcs]
            fcs = [self.get_encape(fc, unit) for fc in fcs]
        else:
            if self.update_env:
                fcs = [EnvFc(unit)]
            else:
                fcs = [RetFc()]
        # if self.update_env and not self.fc:
        #     return UpdateEnvEncape(_args, _eval, unit)
        return ArgsCallEncape(fcs, _args, _eval, unit)
class RetArgsDeal(ArgsCallDeal):
    def init(self):
        super().init(False)
class UpdateEnvDeal(ArgsCallDeal):
    def init(self):
        super().init(False,True)
confs = xf.loads(r"""
# confs.pri: {
#     deal_args: {
#         type=deal
#         src=buildz.argzx.conf_callz.ArgsCallDeal
#         call=1
#         deals=[call,fc]
#     }
# }
confs.pri: [
    (
        (deal, deal_ret)
        buildz.argz.conf_callz.RetArgsDeal
        1,
        [argz_ret,ret]
    )
    (
        (deal, deal_argz_env)
        buildz.argz.conf_callz.UpdateEnvDeal
        1,
        [argz_env,argz_envs]
    )
    (
        (deal, deal_args)
        buildz.argz.conf_callz.ArgsCallDeal
        1,
        [argz,argz_call,argz_fc]
    )
]
builds: [deal_args, deal_ret, deal_argz_env]
""")
class ConfBuilder(Base):
    def init(self, conf=None):
        mg = iocz.build(conf)
        mg.add_conf(confs)
        self.mg = mg
        for key in 'push_var,push_vars,pop_var,pop_vars,set_var,set_vars,get_var,unset_var,unset_vars'.split(","):
            setattr(self, key, getattr(mg,key))
    def adds(self, conf):
        if type(conf)==str:
            conf = xf.loads(conf)
        conf = {'confs': conf}
        self.mg.add_conf(conf)
    def add(self, conf):
        if type(conf)==str:
            conf = xf.loads(conf)
        conf = {'confs': [conf]}
        self.mg.add_conf(conf)
    def call(self, key, args, maps):
        params = argz.Params(args, maps)
        #p = iocz.Params(params=params)
        fc, find = self.mg.get(key)
        #rst, find = self.mg.get(key, params=p)
        assert find, f"key not found: '{key}'"
        return fc(params)[0]
        return rst[0]
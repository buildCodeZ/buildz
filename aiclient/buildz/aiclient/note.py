
from typing import Union, get_type_hints
import inspect
from buildz import dz, log as logz
__doc__="""
package will be focus on buildz.aiclient.skills.{skill_folder}
example:
    skill_folder is demo
    will import like 'from buildz.aiclient.skills.demo import conf'
"""
def types():
    rst = {}
    rst[int] = "integer"
    rst[str]="string"
    rst[float]="float"
    rst[list] = "array"
    rst[object] = "object"
    rst[bool]='boolean'
    return rst
class Demo:
    def fc(self):
        pass

demo=Demo()
type_method = type(demo.fc)
class Note:
    def all(self):
        rst = list(self.conf.values())
        return rst
    def add_type(self, type, name):
        self.types[type] = name
    def __init__(self, log=None):
        self.conf = {}
        self.types = types()
        self.default_type = object
        log = log or logz.simple()
        self.log = log("note")
    def analyze_vars(self, fc, base=-1):
        if base<0:
            base = 1 if isinstance(fc, type_method) else 0
        param_names = fc.__code__.co_varnames[:fc.__code__.co_argcount]
        type_hints = get_type_hints(fc)
        defaults = fc.__defaults__ or ()
        num_defaults = len(defaults)
        num_params = len(param_names)
        default_values = {}
        for i, name in enumerate(param_names):
            if i >= num_params - num_defaults:
                default_values[name] = defaults[i - (num_params - num_defaults)]
        inputs = {}
        reqs = []
        for key in param_names[base:]:
            inputs[key]= {}
            tp = type_hints[key] if key in type_hints else self.default_type
            if tp not in self.types:
                tp = self.default_type
            if key not in default_values:
                reqs.append(key)
            inputs[key]['type']=self.types[tp]
        out = {}
        dz.s(out, type="object", properties=inputs, reqs =reqs)
        return out
    def get(self, fc, base=0):
        #self.log.debug(f"get: {fc}")
        idx = id(fc)
        if idx not in self.conf:
            self.conf[idx] = {}
            self.conf[idx]['@fc']=fc
            self.conf[idx]['inputs'] = self.analyze_vars(fc,base)
        conf = self.conf[idx]
        #self.log.debug(f"get: {conf}")
        return conf
    def skill(self, name, des = None, **maps):
        return self._skill(name, -1, des, **maps)
    def var(self, name, **maps):
        return self._var(name, -1, **maps)
    def var_des(self, **maps):
        return self._var_des(-1, **maps)
    def fc_skill(self, name, des = None, **maps):
        return self._skill(name, 0, des, **maps)
    def fc_var(self, name, **maps):
        return self._var(name, 0, **maps)
    def fc_var_des(self, **maps):
        return self._var_des(0, **maps)
    def mskill(self, name, des=None, **maps):
        return self._skill(name, 1, des, **maps)
    def mvar(self, name, **maps):
        return self._var(name, 1, **maps)
    def mvar_des(self, **maps):
        return self._var_des(1, **maps)
    def _skill(self, name, _base, des = None, **maps):
        def wrap(fc):
            conf = self.get(fc, _base)
            conf['name'] = name
            if des:
                conf['des']=des
            conf.update(maps)
            return fc
        return wrap
    def _var(self, name, _base, **maps):
        def wrap(fc):
            conf = self.get(fc, _base)
            inputs = conf['inputs']['properties']
            inputs[name].update(maps)
            return fc
        return wrap
    def _var_des(self, _base, **maps):
        def wrap(fc):
            conf = self.get(fc, _base)
            inputs = conf['inputs']['properties']
            for k,v in maps.items():
                inputs[k]['des'] = v
            return fc
        return wrap

"""

from buildz.aiclient import note

nt=note.Note()
def f(a,b=0):
    return x

pass
rst = nt.analyze_vars(f)

class A:
    def b(self, v,n=0):
        return v

pass

crst = nt.analyze_vars(A.b)
a=A()

orst = nt.analyze_vars(a.b)

"""
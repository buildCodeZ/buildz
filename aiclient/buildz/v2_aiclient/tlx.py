

from buildz import xf,fz,dz,args as argx, log as logz
from buildz.base import Base
pytype = type
def get_types():
    rst = {}
    rst[int] = "integer"
    rst[str]="string"
    rst[float]="float"
    rst[list] = "array"
    rst[object] = "object"
    rst[bool]='boolean'
    return rst

types=get_types()
class Var(Base):
    def init(self, name, type, des="", need=False, enum=None):
        self.name=name
        if pytype(type)!=str:
            type = types[type]
        self.type = type
        self.des = des
        self.need = need
        self.enum = enum
    @staticmethod
    def build(key, conf, need):
        type, des, enum = dz.g(conf, type=None, des=None, enum=None)
        var = Var(key, type, des, need, enum)
        return var
    def out(self):
        rst = {}
        rst = dz.snn(rst, type=self.type, description=self.des, enum=self.enum)
        return self.name, rst

pass
class Vars(Base):
    def init(self):
        self.vars = []
    def addx(self, **maps):
        return self.add(Var(**maps))
    def add(self, var):
        self.vars.append(var)
        return self
    @staticmethod
    def build(conf):
        assert conf.get("type")=="object"
        vars, reqs = dz.g(conf, properties={}, required=[])
        out = Vars()
        reqs = set(reqs)
        for k,v in vars.items():
            need=k in reqs
            var = Var.build(k,v, need)
            out.add(var)
        return out
    def out(self):
        vars = {}
        reqs = []
        for var in self.vars:
            k,v =var.out()
            vars[k] = v
            if var.need:
                reqs.append(k)
        rst = {'type': 'object', 'properties':vars, 'required': reqs}
        return rst

pass

class Tool(Base):
    @staticmethod
    def build(conf, fc=None):
        assert conf.get("type")=="function"
        name, des = dz.g(conf, name=0, description=0)
        vars = conf.get("parameters", None)
        if vars:
            vars = Vars.build(vars)
        fc = fc or conf.get("@function", None)
        return Tool(name, des, vars, fc)
    def init(self, name=None, des=None, vars=None, fc=None):
        self.name = name
        self.des=des
        self.fc =fc
        self.vars=vars
        self.cache = None
    def set_name(self, name):
        self.name=name
    def set_fc(self, fc):
        self.fc=fc
    def set_vars(self,vars):
        self.vars=vars
    def set_des(self, des):
        self.des=des
    def out(self, simple=False):
        rst = {}
        rst=dz.snn(rst, name=self.name, description=self.des)
        if not simple and self.vars:
            rst['parameters'] = self.vars.out()
        out = dz.maps(type="function", function=rst)
        return out
    def call(self, args):
        try:
            rst = self.fc(**args)
            if rst is None:
                rst = "执行成功"
            return str(rst)
        except Exception as exp:
            #self.log.warn(f"skill '{self.name}' called error: {exp}")
            return f"exception in running skill '{self.name}': {exp}"

pass

class Tools(Base):
    def add_note(self, note):
        confs = note.all()
        for conf in confs:
            tool = Tool.build(conf)
            self.add(tool)
    def add_conf(self, conf, fc=None):
        tool = Tool.build(conf, fc)
        self.add(tool)
    def add_confs(self, confs, fcs=[]):
        for i in range(len(confs)):
            conf = confs[i]
            if i<len(fcs):
                fc = fcs[i]
            self.add_conf(conf, fc)
    def init(self, log=None):
        self.tools = {}
        log = log or logz.simple()
        log = log.sub("tools")
        self.log = log
    def add(self, tool, key=None):
        key = key or tool.name
        self.tools[key] = tool
        return self
    def out(self, simple=False):
        rst = [tool.out(simple) for key,tool in self.tools.items()]
        return rst
    def get(self, key):
        return self.get(key)
    def calls(self, tool_calls):
        rst = [tcall(self) for tcall in tool_calls]
        return rst
    def call(self, key, args):
        if key not in self.tools:
            msg = f"skill '{key}' not found in local"
            return msg
        return self.tools[key].call(args)
        


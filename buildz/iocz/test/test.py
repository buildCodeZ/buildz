#

from buildz import iocz,xf, pyz, Base
wraps = iocz.build_wraps()
ns = wraps('test').wrap
@ns.obj(id='test')
@ns.obj.args("env,PATH")
class Test(Base):
    def str(self):
        return f'Test(<{id(self)}>|id={self.id})'
    def init(self, id=0):
        super().init()
        self.id = id
    def call(self):
        print("Test.show:", self)

pass
#ns.obj.args("env,PATH")(Test)
#ns.obj(id='test')(Test)
var = 'test_var'
confs1 = r'''
ns: xxx
envs: {
    a=0
    b=1
}
confs.ns: [
    [[obj, test1], <buildz>.iocz.test.test.Test, null,{id=[cvar, <buildz>.iocz.test.test.var]}]
    {
        id=test
        type=obj
        source=<buildz>.iocz.test.test.Test
        single=1
        args=[
            #[ref, test1]
            #[env, PATH]
            [ref, test.test]
            
        ]
    }
]
'''.replace("<buildz>", "buildz")
def get_env_sys(self, id, sid=None):
    sysdt = os.getenv(id)
    return sysdt
def test():
    mg = iocz.build()
    wraps.bind(mg)
    print(mg)
    #unit = mg.add_conf(confs)
    unit = mg.add_conf(confs1)
    with mg.push_vars({"test": 123}):
        it, find = unit.get("test")
        print(f"it: {it, id(it)}, find: {find}")
    it, find = unit.get("test")
    print(f"it: {it, id(it)}, find: {find}")
    it, find = mg.get("test", "xxx")
    print(f"it: {it, id(it)}, find: {find}")
    print(f"env: {unit.get_env('b')}")
    print(type(it))
    it = Test(123)
    print(type(it))
    print(it)
    exit()

pyz.lc(locals(), test)
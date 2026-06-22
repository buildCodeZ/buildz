import asyncio
try:
    import async_gaussdb
except ModuleNotFoundError:
    raise Exception("module not found, try: pip install async-gaussdb")
import queue
from .basez import SimpleDv, fetch
from .structz import CMD
from buildz.base import Base
import threading as th
class AsyncGauss(Base):
    def init(self, host, port, user, pwd, database):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.database = database
        self.con = None
        self.trans = None
        self.is_open = False
    async def close(self):
        rst = await self.con.close()
        self.is_open = False
        return rst
    async def connect(self):
        self.con = await async_gaussdb.connect(
            user=self.user,
            password=self.pwd,
            database=self.database,
            host=self.host,
            port=self.port
        )
        self.is_open = True
        return self.con
    async def query(self, sql, vals=()):
        values = await self.con.fetch(sql, *vals)
        return values
    async def execute(self, sql, vals=()):
        return await self.con.execute(sql, *vals)
    async def begin(self):
        self.trans = await conn.transaction()
    async def commit(self):
        await self.trans.commit()
    async def rollback(self):
        await self.trans.rollback()
pass
class Adapter(Base):
    def init(self, host, port, user, pwd, database):
        self.gs = AsyncGauss(host, port, user, pwd, database)
        self.to_async = queue.Queue()
        self.by_async = queue.Queue()
        self.th = None
    def is_open(self):
        return self.th is not None and self.gs.is_open
    def open(self):
        self.th = th.Thread(target=self.async_run,daemon=True)
        self.th.start()
    def async_run(self):
        asyncio.run(self.run())
    def out(self, vals):
        rst = {'value':vals}
        self.by_async.put(rst)
    def exp(self, err):
        rst = {'error': err}
        self.by_async.put(rst)
    async def run(self):
        self.running=True
        while self.running:
            msg = self.to_async.get()
            order = msg[0]
            try:
                if order == "close":
                    await self.gs.close()
                    self.running = False
                    self.out("ok")
                    break
                fc = getattr(self.gs, order)
                rst = await fc(*msg[1:])
                self.out(rst)
            except Exception as exp:
                self.exp(exp)
    def get(self):
        rst = self.by_async.get()
        error = rst.get("error", None)
        if error:
            raise error
        vals = rst.get("value", None)
        return vals
    def close(self):
        self.to_async.put(["close"])
        rst = self.get()
        self.th = None
        return rst
    def connect(self):
        if self.th is None:
            self.open()
        self.to_async.put(["connect"])
        return self.get()
    def query(self, sql, vals=()):
        self.to_async.put(("query", sql, vals))
        return self.get()
    def execute(self, sql, vals=()):
        self.to_async.put(("execute", sql, vals))
        return self.get()
    def begin(self):
        self.to_async.put(["begin"])
        return self.get()
    def commit(self):
        self.to_async.put(["commit"])
        return self.get()
    def rollback(self):
        self.to_async.put(["rollback"])
        return self.get()
pass
class Db(SimpleDv):
    def to_list(self, rst):
        if rst is None:
            return []
        if type(rst)!=list:
            rst = [rst]
        keys = None
        out = []
        for obj in rst:
            tmp = []
            if keys is None:
                keys = []
                for k,v in obj.items():
                    keys.append(k)
                    tmp.append(v)
            else:
                for k in keys:
                    tmp.append(obj[k])
            out.append(tmp)
        out = [keys]+out
        return out
    def init(self):
        self.db = Adapter(self.host,self.port,self.user,self.pwd,self.db)
    def begin(self):
        if self.db.is_open():
            return
        self.db.connect()
    def open(self):
        self.begin()
    def close(self):
        self.db.close()
    def commit(self):
        self.db.commit()
        self.db.close()
        self.db.connect()
    def refresh(self):
        self.db.close()
        self.db.connect()
    def is_open(self):
        return self.db.is_open()
    def query(self, sql, vals=(), as_map = None):
        rst = self.db.query(sql, vals)
        return self.out_list(rst, as_map)
    def execute(self, sql, vals=(), commit=False):
        tmp = self.db.execute(sql, vals)
        if commit:
            self.db.execute("commit;")
        return tmp

pass
def build(argv, conf):
    args = fetch(argv)
    print(f"args: {args}")
    dv = Db(*args)
    return dv

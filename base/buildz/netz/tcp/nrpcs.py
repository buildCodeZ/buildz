from buildz.base import Base
import base64
import json
from buildz import log as logz
from threading import get_ident as gid
import time,random
def uid():
    s = str(time.time())
    bts = os.urandom(6).hex()
    return bts+s
pass
class BaseServer(Base):
    def init(self, skt, log=None):
        log = log or logz.simple()
        self.log = log
        self.skt = skt
        self.sends={}
        self.rst = None
    def out(self, out, msg):
        return out
    def do_deal(self, msg):
        out = self.deal(msg)
        return self.out(out, msg)
    def deal(self, msg):
        assert False, "not impl method deal"
    def send(self, msg=None, tid=None):
        tid = tid or gid()
        out = {'data': msg}
        self.skt.send(out)
        self.sends[tid] = True
    def single(self, tid = None):
        self.rst = None
        tid = tid or gid()
        msg = self.skt.recv()
        self.sends[tid]=False
        if msg is None or len(msg)==0:
            return False, 'null'
        if msg.get("close", False):
            return False, msg.get('msg', 'close')
        if msg.get("break", False):
            return False, msg.get('msg', 'break')
        rst = self.do_deal(msg)
        if not self.sends[tid]:
            self.skt.send(rst)
        return True, None
    def run(self):
        return self.call()
    def call(self):
        tid = gid()
        run = True
        while run:
            run, rst = self.single(tid)
        return rst
class Servers(BaseServer):
    def init(self, skt, log=None, default_obj=None, default_fns=None):
        super().init(skt, log)
        self.objs = {}
        if default_obj:
            self.objs[None] = default_obj, default_fns
    def add(self, obj_key, obj, fns=None):
        self.objs[obj_key] = obj, fns
    def pop(self, obj_key):
        return self.objs.pop(obj_key)
    def deal_rst(self, rst, msg):
        if not msg.get("ret_nrpc", False):
            return rst
        key = msg.get("key_nrpc", None)
        if key is None:
            key = uid()
        self.add(key, rst)
        return {"key_nrpc": key}
    def deal(self, msg):
        obj_key = msg.get("object", None)
        out = {}
        if obj_key not in self.objs:
            out['error'] = f"object {obj_key} not found"
            return out
        obj, fns = self.objs[obj_key]
        fn = msg.get("call")
        if fns is not None and fn not in fns:
            out['error'] = f"method '{fn}' is not allow to called"
            return out
        if not hasattr(obj, fn):
            out['error'] = f"method '{fn}' not exists in obj"
            return out
        args = msg.get("args", [])
        maps = msg.get("maps", {})
        try:
            fc = getattr(obj, fn)
            rst = fc(*args, **maps)
            rst = self.deal_rst(rst, msg)
            out['data'] = rst
        except Exception as exp:
            self.log.error(f"exp: {exp}")
            import traceback as tb
            err = tb.format_exc()
            self.log.error(f"traceback: {err}")
            out['error'] = str(exp)
        return out
class Server(BaseServer):
    def init(self, obj, skt, fns = None, log=None):
        super().init(skt, log)
        self.obj = obj
        if fns is not None:
            if type(fns)==str:
                fns = fns.split(",")
                fns = [k.strip() for k in fns]
            fns = set(fns)
        self.fns = fns
    def deal(self, msg):
        fn = msg.get("call")
        out = {}
        if self.fns is not None and fn not in self.fns:
            out['error'] = f"method '{fn}' is not allow to called"
            return out
        if not hasattr(self.obj, fn):
            out['error'] = f"method '{fn}' not exists in obj"
            return out
        args = msg.get("args", [])
        maps = msg.get("maps", {})
        try:
            fc = getattr(self.obj, fn)
            rst = fc(*args, **maps)
            out['data'] = rst
        except Exception as exp:
            self.log.error(f"exp: {exp}")
            import traceback as tb
            err = tb.format_exc()
            self.log.error(f"traceback: {err}")
            out['error'] = str(exp)
        return out
class Client:
    def __init__(self, clients, key, ret_nrpc=False, rand_nrpc=False):
        self.nrpc_clients = clients
        self.nrpc_key = key
        self.ret_nrpc=ret_nrpc
        self.rand_nrpc = rand_nrpc
    def gen_as(self, key, fn, *args, **maps):
        msg = {'args': args, 'maps': maps}
        msg['call'] = fn
        msg['ret_nrpc']=True
        if key:
            msg['key_nrpc']=key
        rst = self.nrpc_clients.send(msg, self.nrpc_key)
        key = rst['key_nrpc']
        rst = Client(self.clients, key)
        return rst
    def gen(self, fn, *args, **maps):
        return self.gen(None, fn, *args, **maps)
    def __call__(self, fn, *args, **maps):
        msg = {'args': args, 'maps': maps}
        msg['call'] = fn
        rst = self.nrpc_clients.send(msg, self.nrpc_key)
        return rst
    def __getattr__(self, fn):
        def wfc(*args, **maps):
            return self.__call__(fn, *args, **maps)
        return wfc
    def breaks(self, msg=None):
        out = {'break':True}
        if msg is not None:
            out['msg'] = msg
        self.clients.send(out)
    def close(self, msg=None):
        out = {'close':True}
        if msg is not None:
            out['msg'] = msg
        self.clients.send(out)
        self.skt.close()
class Clients(Base):
    @staticmethod
    def single(self, skt, key=None):
        clients = Clients(skt)
        return clients.get_inst(key)
    def init(self, skt):
        self.skt=skt
    def send(self, msg, key=None):
        msg['object'] = key
        self.skt.send(msg)
        rst = self.skt.recv()
        err = rst.get("error", None)
        if err:
            raise Exception(err)
        return rst.get('data', None)
    def get_inst(self, key):
        return Client(self, key)

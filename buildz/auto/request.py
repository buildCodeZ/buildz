#

from ..tools import *
from buildz.ioc import wrap
import json

try:
    import requests as rq
    session = rq.session()
except:
    rq = None
    session = None

pass
class Request(Base):
    def init(self, http_type, use_session, log, upd):
        self.type = http_type
        self.use_session = use_session
        self.log = log
        self.upd = upd
        self.fc = None
        self.fcs = None
        self.key_data = None
        self.build()
    def build(self):
        fcs = {}
        global rq, session
        if rq is None:
            return
        obj = rq
        if self.use_session:
            obj = session
        fcs['get'] = [obj.get, "params"]
        fcs['post'] = [obj.post, "data"]
        fcs['json'] = [obj.post, "json"]
        fcs['put'] = [obj.put, "json"]
        fcs['delete'] = [obj.delete, 'json']
        self.fcs = fcs
        self.fc = self.fcs[self.type][0]
        self.key_data = self.fcs[self.type][1]
    def get_set(self, data, kd, maps, km):
        v = xf.get(data, kd)
        if v is not None:
            maps[km] = v
    def req(self, data):
        url = xf.g(data, url=None)
        maps = {}
        self.get_set(data, "data", maps, self.key_data)
        self.get_set(data, "cookies", maps, "cookies")
        self.get_set(data, "headers", maps, "headers")
        self.get_set(data, "proxies", maps, "proxies")
        return self.fc(url, **maps)
    def rsp(self, rp, data):
        url = xf.g(data, url=None)
        xf.s(data, status_code = rp.status_code)
        xf.s(data, result_code = rp.status_code)
        try:
            xf.s(data, result_content=rp.content)
            s = xf.decode(rp.content, "utf-8")
            xf.s(data, result_text=s)
        except Exception as exp:
            self.log.warn(f"exp in deal response on '{url}': {exp}")
        try:
            obj = json.loads(s)
            xf.s(data, result=obj)
        except Exception as exp:
            #self.log.warn(f"exp in deal response on '{url}': {exp}")
            pass
        try:
            xf.s(data, result_cookies=dict(rp.cookies))
        except Exception as exp:
            self.log.warn(f"exp in deal response on '{url}': {exp}")
        try:
            xf.s(data, result_headers = dict(rp.headers))
        except Exception as exp:
            self.log.warn(f"exp in deal response on '{url}': {exp}")
        return True
    def call(self, data, fc=None):
        if self.fc is None:
            self.log.error("install requests to use this(pip install requests)")
            return False
        if self.upd is not None:
            data = self.upd(data)
        url = xf.g(data, url=None)
        try:
            rp = self.req(data)
        except Exception as exp:
            self.log.error("error in request '{url}' with method {self.type}: {exp}")
            return False
        self.rsp(rp, data)
        if fc is None:
            return True
        return fc(data)

pass


@wrap.obj(id="request.post")
@wrap.obj_args("post", "env, request.session, false", "ref, log", "ref, cache.modify")
class Post(Request):
    pass

pass

@wrap.obj(id="request.json")
@wrap.obj_args("json", "env, request.session, false", "ref, log", "ref, cache.modify")
class Json(Request):
    pass

pass

@wrap.obj(id="request.get")
@wrap.obj_args("get", "env, request.session, false", "ref, log", "ref, cache.modify")
class Get(Request):
    pass

pass

@wrap.obj(id="request.put")
@wrap.obj_args("put", "env, request.session, false", "ref, log", "ref, cache.modify")
class Put(Request):
    pass

pass

@wrap.obj(id="request.delete")
@wrap.obj_args("delete", "env, request.session, false", "ref, log", "ref, cache.modify")
class Delete(Request):
    pass

pass

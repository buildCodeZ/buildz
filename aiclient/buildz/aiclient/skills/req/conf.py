
from buildz.aiclient import note
from buildz import fz, log as logz, base, dz
#import os
from os.path import join,expanduser,realpath
from os import listdir
from re import findall
import requests as rq
n = note.Note()
get_cache = None
log=None
@n.skill("http.get", "调用http的get方法，访问网站页面，读取页面数据，可以指定读取页面数据的一部分而不是全部")
@n.var_des(
    url="网站链接地址",
    headers="请求头信息，json字典，默认为空字典:{}",
    coding="网站内容编码，默认utf-8",
    base="页面数据从该位置开始读取，默认0",
    last="页面数据读取到该位置截止，默认读取到页面结束",
    reuse="是否复用缓存，如果是，并且之前调用过对应的链接，则不再次调用而是用之前缓存的页面内容，默认true"
)
def wrap_get(url:str, headers={}, coding:str="utf-8", base:int=0, last:int=-1, reuse:bool=True):
    id = f"get({url}){headers}"
    fc = lambda: get(url, headers, coding)
    content = get_cache(id, fc, base,last,reuse)
    log.info(f"get '{url}'[{base}:{last}] return: {len(content)} bytes")
    return content
def get(url:str, headers={}, coding:str="utf-8"):
    rp = rq.get(url, headers=headers)
    if rp.status_code!=200:
        raise Exception(f"'{url}'访问报错：{rp.status_code}")
    content = rp.content.decode(coding)
    return content


pass

@n.skill("http.post", "调用http的post方法，可以传递json参数，返回的数据可以指定只读取一部分而不是全部")
@n.var_des(
    url="网站链接地址",
    json="传递的数据，要求json格式字典",
    headers="请求头信息，json字典，默认为空字典:{}",
    coding="网站内容编码，默认utf-8",
    base="返回数据从该位置开始读取，默认0",
    last="返回数据读取到该位置截止，默认读取到数据结束",
    reuse="是否复用缓存，如果是，并且之前调用过对应的链接，则不再次调用而是用之前缓存的页面内容，默认true"
)
def wrap_post(url:str, json={}, headers={}, coding:str="utf-8", base:int=0, last:int=-1, reuse:bool=True):
    id = f"post({url}){headers}:{json}"
    fc = lambda: post(url, json, headers, coding)
    content = get_cache(id, fc, base,last,reuse)
    log.info(f"post '{url}'[{base}:{last}] return: {len(content)} bytes")
    return content
def post(url:str, json, headers={}, coding:str="utf-8"):
    rp = rq.post(url, json=json, headers=headers)
    if rp.status_code!=200:
        raise Exception(f"'{url}'访问报错：{rp.status_code}")
    content = rp.content.decode(coding)
    return content

pass

# all=n.all()
def build(tools):
    global log,get_cache
    log = tools.log("skills.req")
    get_cache = tools.caches.sub("skills.req")
    return n.all()
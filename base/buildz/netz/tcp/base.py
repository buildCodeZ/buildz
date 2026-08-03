
import socket, select, traceback, threading, time, os
from buildz.base import Base
from buildz import log as logz, pyz, xf, fz
from buildz import args as argx
def fetch_addr(addr):
    if type(addr)!=str:
        return addr
    if addr.find(":")<0:
        return addr
    ip, port = addr.split(":")
    port = int(port)
    return (ip, port)
def new_skt(addr):
    if type(addr)==str:
        if os.path.isfile(addr):
            os.remove(addr)
        skt = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    else:
        skt = socket.socket()
    return skt
def mstr(data):
    if type(data) not in (str, bytes):
        return data
    sz = len(data)
    if sz<12:
        return str(data)
    data = str(data)[:10]
    rs = f"{data}...{str(sz)}"
    return rs
def dsp(data):
    if type(data)==dict:
        rst = {}
        for k,v in data.items():
            v = mstr(v)
            rst[k] = v
        data = rst
    elif type(data) in (str, bytes):
        data = mstr(data)
    return data

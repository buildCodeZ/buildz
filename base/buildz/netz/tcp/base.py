
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

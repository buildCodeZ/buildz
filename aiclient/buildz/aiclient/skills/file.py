
from buildz import dz
from buildz.aiclient import note
from buildz import fz, log as logz, base, dz
import os
from os.path import join,expanduser,realpath
from os import listdir
from re import findall
ac = note.Note()
path_check = None
log=logz.simple()
get_cache=None
@ac.skill("file.read", "读取文本文件内容，默认只读取1024字节的文件,可以自定义读取多少,从哪里开始读取")
@ac.var_des(
    fp="文件路径",
    coding="文件编码格式，默认utf-8",
    base="文本数据从该位置开始读取，默认0",
    last="文本数据读取到该位置截止，传入大于0的整数,或-1表示读取到文本结束,默认-1",
    max_size="读取的最多字节数,当数据大于max_size,会截取前max_size部分的数据,默认1024"
)
def wrap_read(fp:str, coding:str="utf-8", base:int=0, last:int=-1, max_size:int=1024):
    s = read(fp, coding)
    if last>0:
        s = s[:last]
    if base > 0:
        s =s[base:]
    data=s
    data = data[:max_size]
    log.info(f"read '{fp}'[{base}:{last}]: {len(data)} bytes")
    rst = f"{data}\n读取内容如上,应返回{len(s)}字节,实际返回{len(data)}字节"
    if len(data)!=len(s):
        rst+=",实际返回因为max_size参数被截断"
    return rst
def read(fp:str, coding:str="utf-8"):
    path_check.check(fp)
    data = fz.read(fp).decode(coding)
    return data

pass

@ac.skill("file.write", "往文件里写入/修改文本数据，文件不存在会新建")
@ac.var_des(
    s="文本数据内容",
    fp="文件路径",
    coding="文件编码格式，默认utf-8",
    base="要插入/修改内容的开始位置,大于等于0的整数",
    last="要插入/修改内容的结束位置,大于等于0的整数,以及-1表示从base到文件末尾都替换掉,和base一样则表示是插入",
)
def write(s: str, fp:str, coding:str="utf-8", base:int=0, last:int=-1):
    path_check.check(fp)
    fz.makefdir(fp)
    md=s
    if os.path.isfile(fp):
        s = read(fp, coding)
    else:
        s = ""
    prefix = s[:base]
    suffix = s[base:]
    if last>=0:
        suffix = s[:last]
    s = prefix+md+suffix
    md='wb'
    fz.write(s.encode(coding), fp, md)

@ac.skill("file.list", "遍历路径下的文件/文件夹，返回文件/文件夹列表")
@ac.var_des(
    path="要遍历的路径"
)
def list(path:str):
    path_check.check(path)
    return listdir(path)

pass

@ac.skill("file.mkdir", "创建文件夹，文件夹的前置路径不存在也会创建")
@ac.var_des(
    path="文件夹路径"
)
def mkdir(path:str):
    path_check.check(path)
    fz.makedir(path)

@ac.skill("file.remove", "删除文件/文件夹，如果文件夹下有其他文件/文件夹，会一起被删除")
@ac.var_des(
    path="文件/文件夹路径"
)
def remove(path):
    path_check.check(path)
    fz.removes(path)

class Check(dz.Check):
    '''
        限制程序可以访问的文件/文件夹
    '''
    def init(self, log, path):
        self.log = log("file.check")
        super().init([path], [], False, self.fc_checks)
    def fc_checks(self, path, paths):
        path = realpath(expanduser(path))
        for _path in paths:
            _path = realpath(expanduser(_path))
            if path.find(_path)==0:
                return True
        return False
    def check(self, path):
        if not self.call(path):
            raise Exception(f"'{path}' is not visitable")

pass
def build_note(path=".", _log=None):
    global log, path_check
    log = _log or logz.simple()
    path_check = Check(log, path)
    return ac

def build(path=".", _log=None):
    return build_note(path, _log).out()


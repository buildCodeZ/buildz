
from buildz.aiclient import note
from buildz import fz, log as logz, base, dz
#import os
from os.path import join,expanduser,realpath
from os import listdir
from re import findall
ac = note.Note()
path_check = None
log=None
get_cache=None
@ac.skill("file.read", "读取文本文件内容，可以指定读取文本数据的一部分而不是全部")
@ac.var_des(
    fp="文件路径",
    coding="文件编码格式，默认utf-8",
    base="文本数据从该位置开始读取，默认0",
    last="文本数据读取到该位置截止，默认读取到文本结束"
)
def wrap_read(fp:str, coding:str="utf-8", base:int=0, last:int=-1):
    data = get_cache(fp, lambda:read(fp, coding), base,last,True)
    log.info(f"read '{fp}'[{base}:{last}]: {len(data)} bytes")
    return data
def read(fp:str, coding:str="utf-8"):
    path_check.check(fp)
    data = fz.read(fp).decode(coding)
    return data

pass

@ac.skill("file.write", "往文件里写入文本数据，文件不存在会新建")
@ac.var_des(
    s="文本数据内容",
    fp="文件路径",
    coding="文件编码格式，默认utf-8",
    # append="如果文件已存在，是否在文件末尾添加，true表示在已有文件末尾增加内容，false表示替换已有文件，默认false"
)
def write(s: str, fp:str, coding:str="utf-8"):#,append:bool=False):
    path_check.check(fp)
    fz.makefdir(fp)
    md='wb'
    # if append:
    #     md = 'ab'
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

class Check(base.Base):
    '''
        限制程序可以访问的文件/文件夹
    '''
    def rpath(self, path):
        if type(path)==str:
            return realpath(expanduser(path))
        ptype, path = path
        if ptype=='skills':
            path = join(self.pkg_dir, path)
        elif ptype=='aiclient':
            path = join(self.skills_dir, path)
        return realpath(expanduser(path))
    def init(self, log, pkg_dir, skills_dir, **maps):
        self.log = log("file.check")
        self.pkg_dir = pkg_dir
        self.skills_dir = skills_dir
        dz.conf2obj(self, maps, whitelist=[], blacklist=[], default_pass=False, white_pattens=[], black_pattens=[])
        self.whitelist=[self.rpath(k) for k in self.whitelist]
        self.blacklist=[self.rpath(k) for k in self.blacklist]
        self.empty = (len(self.whitelist)+len(self.blacklist)+len(self.white_pattens)+len(self.black_pattens))==0
        self.log.debug(f"check empth: {self.empty}")
    def call(self, path):
        if self.empty:
            self.log.debug(f"check empty: <{path}>")
            return True
        path = self.rpath(path)
        self.log.debug(f"check path: <{path}>")
        for _pth in self.whitelist:
            self.log.debug(f"<{path}> check whitelist '{_pth}'")
            if path.find(_pth)==0:
                return True
        for pt in self.white_pattens:
            self.log.debug(f"<{path}> check white_patten '{pt}'")
            if len(findall(pt, path))>0:
                return True
        for _pth in self.blacklist:
            self.log.debug(f"<{path}> check blacklist '{_pth}'")
            if path.find(_pth)==0:
                return False
        for pt in self.black_pattens:
            self.log.debug(f"<{path}> check black_patten '{pt}'")
            if len(findall(pt, path))>0:
                return False
        self.log.debug(f"<{path}> check default_pass '{self.default_pass}'")
        return self.default_pass
    def check(self, path):
        if not self.call(path):
            raise Exception(f"'{path}' is not visitable")

pass

def build(tools):
    global log,get_cache,path_check
    log = tools.log("skills.file")
    get_cache = tools.caches.sub("skills.file")
    conf = tools.get_profile()
    conf = conf.get("file_profile", {})
    path_check = Check(tools.log, tools.pkg_dir, tools.dp, **conf)
    return ac.all()


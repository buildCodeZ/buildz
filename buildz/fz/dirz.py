#coding=utf-8
import os
#列出文件夹下所有文件和文件更新时间
#文件访问处理方法
#建议visit读取文件
#catch处理目录访问异常
class FileDeal:
    def __init__(self, *argv, **maps):
        self.init(*argv, **maps)
    def result(self):
        return None
    def init(self, *argv, **maps):
        pass
    def work(self, *argv, **maps):
        return self.dirs(*argv, **maps)
    def dirs(self, filepath, depth = 0):
        dirs(filepath, self, depth)
        return self.result()
    def visit(self, filepath, isdir, depth):
        return True
    def catch(self, filepath, isdir, depth, exp):
        pass
    def deal(self, filepath, isdir, depth, exp = None):
        if exp is None:
            return self.visit(filepath, isdir, depth)
        else:
            return self.catch(filepath, isdir, depth, exp)
    def __call__(self, *argv, **maps):
        return self.deal(*argv, **maps)

pass
#遍历文件／文件夹filepath
def dirs(filepath, fc=FileDeal(), depth = 0):
    isdir = os.path.isdir(filepath)
    visit = fc(filepath, isdir, depth)
    if isdir and visit:
        try:
            files = os.listdir(filepath)
        except Exception as exp:
            fc(filepath, isdir, depth, exp)
            return
        files = [os.path.join(filepath, file) for file in files]
        [dirs(fp, fc, depth+1) for fp in files]

pass


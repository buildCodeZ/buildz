#coding=utf-8

from buildz.xconfz.mg import *
from buildz.xconfz.mg_fmt import *
from buildz.xconfz.file import *

"""
loads(string) => object

dumps(object, format = False, simple = 1, as_json = False, t_single = True) => string
format: 是否格式化
as_json: 数值用json方法生成
t_single: 字符串中换行改成\n


loadfile(filepath, coding = 'utf-8') => object
= loads(fread(filepath, coding))

fread(filepath, coding = 'utf-8') => string
二进制读取文件并用coding编码，编码失败会换另一个编码尝试(gbk)
"""
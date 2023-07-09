#coding=utf-8

coding="utf-8"
def bread(filepath):
    with open(filepath, 'rb') as file:
        s = file.read()
    return s

pass
def decode(s, coding = 'utf-8'):
    coding = coding.lower()
    xcoding = 'utf-8'
    if coding == 'utf-8':
        xcoding = 'gbk'
    try:
        return s.decode(coding)
    except:
        return s.decode(xcoding)

pass
def decode_c(s, coding = 'utf-8'):
    coding = coding.lower()
    xcoding = 'utf-8'
    if coding == 'utf-8':
        xcoding = 'gbk'
    try:
        return s.decode(coding), coding
    except:
        return s.decode(xcoding), xcoding

pass
def fread(filepath, coding = 'utf-8'):
    s = bread(filepath)
    return decode(s, coding)

pass
def fread_c(filepath, coding = 'utf-8'):
    s = bread(filepath)
    return decode_c(s, coding)

pass
import struct
class Block:
    '''
        在网络流数据上使用格式"数据长度+数据"，数据长度用4字节整数
    '''
    def __init__(self):
        self.caches = b""
        self.build = self.wrap
    def empty(self):
        return len(self.caches)==0
    def clean(self):
        self.caches = b''
    def get(self, bts=b""):
        '''
            返回数据和缓存剩余大小
            缓存数据不足以返回单个数据时，返回的数据为b''
        '''
        if bts!=b'':
            self.caches+=bts
        lc = len(self.caches)
        if lc<4:
            return b"", lc
        bsz = self.caches[:4]
        sz = struct.unpack("<I", bsz)[0]
        if lc<sz+4:
            return b'', lc
        dts = self.caches[4:4+sz]
        self.caches = self.caches[4+sz:]
        return dts, len(self.caches)
    def wrap(self, bts):
        '''
            输入数据
            返回"数据长度+数据"，数据长度4字节
        '''
        sz = len(bts)
        bsz = struct.pack("<I", sz)
        return bsz+bts

pass


class BufferInput:
    def __init__(self, buf):
        self.buf = buf
    def __call__(self, size=1):
        s = self.buf[:size]
        self.buf = self.buf[size:]
        return s

pass

class Buffer:
    def read(self, size = 1, pop = 0):
        if self.s_read is None:
            self.s_read = self.input(1)
        l = len(self.s_read)
        if l<size:
            self.s_read += self.input(size-l)
        rst = self.s_read[:size]
        if pop:
            self.s_read = self.s_read[size:]
        if self.buffer is None:
            self.buffer = self.s_read[:0]
        return rst
    def pop_read(self, size=1):
        self.s_read = self.s_read[size:]
    def init(self):
        self.buffer = None
        self.s_read = None
    def __init__(self, input):
        self.input = input
        self.init()
    def add(self, arr):
        if self.buffer is None:
            self.buffer = arr
        else:
            self.buffer += arr
    def size(self):
        if self.buffer is None:
            return 0
        return len(self.buffer)
    def full(self, size = 0, right = 1):
        if right:
            return self.rfull(size)
        return self.lfull(size)
    def clean(self):
        self.buffer = self.buffer[:0]
    def get(self, size=1, right=1):
        if right:
            return self.rget(size)
        return self.lget(size)
    def pop(self, size=1, right=1):
        if right:
            return self.rpop(size)
        return self.lpop(size)
    def lfull(self, size = 0):
        if self.buffer is None:
            return self.buffer
        if size == 0:
            return self.buffer
        return self.buffer[size:]
    def rfull(self, size = 0):
        if self.buffer is None:
            return self.buffer
        if size == 0:
            return self.buffer
        return self.buffer[:-size]
    def lget(self, size=1):
        if self.buffer is None:
            return self.buffer
        return self.buffer[:size]
    def rget(self, size=1):
        if self.buffer is None:
            return self.buffer
        return self.buffer[-size:]
    def lpop(self, size = 1):
        if self.buffer is None:
            return self.buffer
        self.buffer = self.buffer[size:]
    def rpop(self, size=1):
        if self.buffer is None:
            return self.buffer
        self.buffer = self.buffer[:-size]

pass

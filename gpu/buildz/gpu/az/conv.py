
from buildz.base import Base
from .util import *
class Conv(Base):
    """
        [batch, channel, dim1, dim2, ...]
    """
    def init(self, dims, ch_in, ch_out, kernel, bias=True, stride=1, padding=0):
        self.ch_in = ch_in
        self.ch_out = ch_out
        self.dims = dims
        self.bias=bias
        self.kernel = exp(kernel, dims)
        self.stride=exp(stride, dims)
        self.padding=exp(padding, dims)
    def fetch(self, shape):
        if type(shape)==int:
            shape = [shape]
        shape = list(shape)
        while len(shape)<self.dims+2:
            shape = [1]+shape
        batch = shape[0]
        ch = shape[1]
        return batch,ch, shape[2:]
    def out(self, shape):
        batch, ch, szs = self.fetch(shape)
        outs = [batch, self.ch_out]
        for kernel_size, stride, padding, dim_in in zip(self.kernel, self.stride, self.padding, szs):
            val = int((dim_in - kernel_size + 2*padding)/stride)+1
            outs.append(val)
        return outs
    def cache(self, shape, unit=1):
        # shape = [batch, channel, dim1, dim2, ...]
        batch, ch, szs = self.fetch(shape)
        n_input = batch*ch*mul(shape[2:])
        n_w = self.ch_out*self.ch_in*mul(self.kernel)
        n = n_input+n_w
        return n*unit
    def cal(self, shape):
        out = self.out(shape)
        batch = shape[0]
        ch = shape[1]
        out_szs = shape[2:]
        n = mul(out_szs)*self.ch_out*self.ch_in*mul(self.kernel)*2
        return n
    def backcal(self, batch=1):
        return 2*self.cal(batch)
    def size(self, unit=1):
        n = self.ch_in*self.ch_out*mul(self.kernel)+self.bias*self.ch_out
        return n*unit

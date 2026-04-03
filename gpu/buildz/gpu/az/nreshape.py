
from torch import nn
from . import util
class ReshapeModule(nn.Module):
    def __init__(self, shape, cal_batch=False):
        super().__init__()
        self.shape = shape
        self.cal_batch = cal_batch
        self.size = 0
        if cal_batch:
            self.size = util.mul(shape)
    def forward(self, inputs):
        if self.cal_batch:
            isize = util.mul(inputs.size())
            n = isize//self.size
            shape = [n]+list(self.shape)
        else:
            shape = self.shape
        inputs = inputs.reshape(shape)
        return inputs

def reshape(shape, cal_batch=False):
    return ReshapeModule(shape, cal_batch)
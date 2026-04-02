
from torch import nn
class ReshapeModule(nn.Module):
    def __init__(self, shape):
        super().__init__()
        self.shape = shape
    def forward(self, inputs):
        inputs = inputs.reshape(self.shape)
        return inputs

def reshape(shape):
    return ReshapeModule(shape)
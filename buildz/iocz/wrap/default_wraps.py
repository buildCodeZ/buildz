#

from . import obj

def build(wraps):
    wraps.set_fc("obj", obj.ObjectWrap())
    return wraps

pass
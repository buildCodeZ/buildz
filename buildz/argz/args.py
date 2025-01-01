#

from buildz import xf, Base

class Args(Base):
    """
        order: [0, cal]
        args: [(1,), []]
        maps: {
            
        }
    """
    def init(self, conf):
        if type(conf)==str:
            conf = xf.loads(conf)
        self.conf = conf
    def call(self, argx):
        
        pass
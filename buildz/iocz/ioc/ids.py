from .base import Base
class Ids(Base):
    '''
    '''
    def init(self, spt):
        self.spt = spt
    def id(self, *ids):
        if len(ids)==0:
            return None
        elif len(ids)==1:
            if type(ids[0]) in (list, tuple):
                ids = ids[0]
        return self.spt.join(ids)
    def ids(self, id):
        if type(id) in (list, tuple):
            return id
        return id.split(self.spt)
    def call(self, a,b):
        a = self.ids(a)
        b = self.ids(b)
        return self.id(a,b)
pass


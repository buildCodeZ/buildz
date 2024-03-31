#
from ..ioc.base import Base, EncapeData

class ValDeal(Base):
    """
    {
        val: ...
    }
    """
    def deal(self, edata:EncapeData):
        data = edata.data
        if type(data)==list:
            return data[-1]
        return data['val']

pass

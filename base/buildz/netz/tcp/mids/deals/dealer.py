
from .base import *

class MidDealer(Base):
    '''
        mid处理中心节点，只作为框架，可以添加不同指令和对应的处理方法
    '''
    def init(self, mskt, slt, deals_send = [], deals_recv = []):
        self.deals_send = deals_send
        self.deals_recv = deals_recv
        self.mskt = mskt
        self.slt = slt
        self.deals= {}
        self.closes = []
        self.deals_timeout = []
        self.deals_closed=[]
    def add_timeout(self, fc):
        self.deals_timeout.append(fc)
    def deal_timeout(self):
        for fc in self.deals_timeout:
            fc()
    def add_closed(self, fc):
        self.deals_closed.append(fc)
    def deal_closed(self):
        for fc in self.deals_closed:
            fc()
    def add_close(self, fc):
        self.closes.append(fc)
    def close(self):
        for fc in self.closes:
            fc()
        self.mskt.close()
    def set_deal(self, _type, fc):
        self.deals[_type] = fc
    def call(self, opt):
        return self.deal_by_slt(opt)
    def deal_by_slt(self, opt):
        if opt == Selector.TIMEOUT:
            self.deal_timeout()
            return
        if opt==Selector.CLOSED:
            self.deal_closed()
            return
        msg = self.recv()
        if self.deal_by_msg(msg):
            return
        while self.mskt.readable():
            msg = self.recv()
            if self.deal_by_msg(msg):
                return
    def deal_by_msg(self, data):
        if data==b'':
            self.close()
            return True
        _type = data['type']
        assert _type in self.deals, f'{_type} not in {self}.deals'
        return self.deals[_type](data)
    def recv(self):
        msg = self.mskt.recv()
        for deal in self.deals_recv:
            msg = deal(msg)
        return msg
    def send(self, msg):
        for deal in self.deals_send:
            msg = deal(msg)
        self.mskt.send(msg)

pass


class MidDealers(MidDealer):
    '''
        增加添加子节点
    '''
    def init(self, mskt, slt, deals_recv=[], deals_send=[], call_by_slt=False):
        super().init(mskt, slt, deals_recv, deals_send)
        self.call_by_slt=call_by_slt
        self.dealers = {}
    def set_dealers(self, nid, dealer):
        self.dealers[nid] = dealer
        self.add_close(dealer.close)
        self.add_closed(dealer.closed)
        self.add_timeout(dealer.timeout)
    def deal_by_msg(self, msg):
        _tpye, nid = dz.g(msg, type=None, nid=None)
        if nid is None:
            return super().deal_by_msg(msg)
        return self.dealers[nid](msg)
    def call(self, data):
        if self.call_by_slt:
            assert type(data)==str
            return self.deal_by_slt(data)
        else:
            return self.deal_by_msg(data)

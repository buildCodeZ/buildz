
from .base import *

class MidTransMg(Base):
    '''
        注册id，可以以一个mid为中间节点，两个mid进行传输
        因为mid_srv有多个mid_dealer，MidTrans创建独立于mid_dealer，只是每个mid_dealer创建的时候调用MidTrans的对应方法
    '''
    def init(self):
        self.mids = {}
    def regist(self, dealer, mid=None):
        MidTrans(dealer, mid, self, False)
    def regist_trans(self, mid, trans):
        self.mids[mid] = trans

class MidTrans(Base):
    def init(self, dealer, mid=None, mg=None, is_dealer=True):
        self.mg = mg
        self.dealer=dealer
        self.mid=mid
        self.is_dealer = is_dealer
        dealer.set_deal('trans.send', self.deal_send)
        dealer.set_deal('trans.regist', self.deal_regist)
        if is_dealer:
            self.remote_regist()
    def remote_regist(self):
        assert self.mid is not None 
        dealer.send(dz.mnn(mid=self.mid, type="trans.regist"))
    def deal_regist(self, msg):
        assert self.mid is None
        mid = dz.g(msg, mid=None)
        assert mid is not None
        self.mid = mid
        self.mg.regist_trans(mid, self)
    def send(self, msg, mid):
        assert mid == self.mid
        msg['src'] = mid
        self.dealer.send(msg)
    def deal_send(self, msg):
        '''
            处理转发
            只做单次转发
            如果自身是接收方
        '''
        mid = dz.g(msg, mid=0)
        if mid != self.mid or not self.is_dealer:
            mid_trans = self.mg.get(mid)
            mid_trans.send(msg, self.mid)
            return
        

pass



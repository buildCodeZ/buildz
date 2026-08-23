from .base import *
class MidPing(Base):
    def init(self, dealer):
        self.dealer = dealer
        self.regist(dealer)
    def ping(self):
        self.dealer.send(dz.mnn(type='ping'))
    def regist(self, dealer):
        dealer.set_deal('ping', self.deal_ping)
        dealer.set_deal('pong', self.deal_pong)
        dealer.add_timeout(lambda :self.ping())
    def deal_ping(self, data):
        self.dealer.send(dz.mnn(type='pong'))
    def deal_pong(self, data):
        pass

pass



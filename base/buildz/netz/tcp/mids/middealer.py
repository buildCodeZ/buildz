
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
    def deal(self, opt):
        if opt == Selector.TIMEOUT:
            self.deal_timeout()
            return
        if opt==Selector.CLOSED:
            self.deal_closed()
            return
        msg = self.mskt.recv()
        for deal in self.deals_recv:
            msg = deal(msg)
        if self.single_deal(msg):
            return
        while self.mskt.readable():
            msg = self.mskt.recv()
            if self.single_deal(msg):
                return
    def single_deal(self, data):
        if data==b'':
            self.close()
            return True
        _type = data['type']
        assert _type in self.deals, f'{_type} not in {self}.deals'
        return self.deals[_type](data)
    def send(self, msg):
        for deal in self.deals_send:
            msg = deal(msg)
        self.mskt.send(msg)

pass
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

class MidListen(Base):
    '''
        本地连接监听
        收到连接请求后往另一个mid发送连接请求，建立通道，直接传输数据
    '''
    def init(self, dealer, addr, listen_num=100):
        self.dealer = dealer
        self.listen_num = listen_num
        self.addr = fetch_addr(addr)
        self.addr = addr
        self.server = new_skt(self.addr)
        self.server.bind(self.addr)
        self.server.listen(self.listen_num)
        self.server_id = self.slt.add(self.server, self.deal_server)
        self.clis = {}
        self.cli_id = 0
    def deal_server(self, opt):
        '''
            本地监听到新连接的处理方法:
                新建本地客户端连接处理，往远端中间件发送新建连接请求，等待响应处理
        '''
        if opt!=Selector.READABLE:
            if opt==Selector.CLOSED:
                # 本地监听被中断，结束
                self.close()
            return
        skt, addr = self.server.accept()
        self.deal_server_skt(skt, addr)
    def deal_server_skt(self, skt, addr):
        self.log.debug(f"accept: {skt}, {addr}")
        _id = self.id
        self.id+=1
        self.clis[_id]=[skt, addr, 0, -1]#slt_id]
        #slt_id = self.slt.add(skt, self.wrap_cli(_id))
        self.log.debug(f"before send connect: {self.mid_skt}, {addr}")
        self.mid_skt.send({"type":"connect", 'id': _id})
        self.log.debug(f"done send connect: {self.mid_skt}, {addr}")

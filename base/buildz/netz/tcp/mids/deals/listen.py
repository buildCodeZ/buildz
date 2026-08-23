
from .base import *
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

from buildz.tls import *

class Server(Base):
    def init(self, conf, inst):
        addr = tuple(conf.gets("ip,port", "127.0.0.1", 8080))
        self.addr = addr
        self.make_deal = confz.get(inst,"server.deal")
        skt = socket.socket()
        skt.listen(addr)
        self.skt = skt
        self.running = True
        self.thread = None
    def stop(self):
        self.running = False
    def start(self):
        t = th.Thread(target=self.listen, daemon=True)
        t.start()
        self.thread = t
    def join(self):
        self.thread.join()
    def listen(self):
        self.running = True
        while self.running:
            skt = self.skt.accept()
            if not skt:
                continue
            t = th.Thread(target=self.make_deal(skt, self),daemon=True)
            t.start()
            self.tds.append(t)
        for t in self.tds:
            t.join()
    def call(self):
        self.listen()
pass


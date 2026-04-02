#
'''
quest
verify

skt.wrap()

skt.input.add()
skt.ouput.add()

Pub(密码1，密码2，数据)

密码(数据)


'''
class Deal(Base):
    def init(self):
        self.deals = {}
    def call(self, skt, server):
        order = skt.get()
        self.deals[order](skt, server)

pass
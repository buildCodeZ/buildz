from html.parser import HTMLParser
from .. import xf
from ..base import Base
import re
class HtmlTag:
    def data(self):
        return self.to_maps()
    def to_maps(self):
        nodes = [n.to_maps() for n in self.nodes]
        rst = {'tag': self.tag, 'attrs': self.attrs, 'nodes': nodes}
        return rst
    def __str__(self):
        return xf.dumps(self.to_maps())
    def __repr__(self):
        return self.__str__()
    def tags(self, tag):
        rst=[]
        for nd in self.nodes:
            if not is_node(nd):
                continue
            if nd.tag==tag:
                rst.append(nd)
            rst+=nd.tags(tag)
        return rst
    def get(self, key, default=None):
        return self.attrs.get(key, default)
    def __init__(self, tag, attrs=None):
        self.tag = tag
        if attrs is None:
            attrs = {}
        self.attrs = attrs
        self.nodes = []
        self.text = None
        self.maps = {}
    def add_node(self, node):
        tag = node.tag
        if tag not in self.maps:
            self.maps[tag] = []
        self.maps[tag].append(node)
        self.nodes.append(node)
    def add_text(self, text):
        text = text.strip()
        self.text = text
        self.nodes.append(text)
    def texts(self):
        rst =[]
        for nd in self.nodes:
            if type(nd)==HtmlTag:
                nd = nd.texts()
            rst.append(nd)
        return "".join(rst)

pass

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = HtmlTag("document")
        self.stacks = [self.data]
    def handle_comment(self, data):
        "处理注释，< !-- -->之间的文本"
        pass
    def handle_startendtag(self, tag, attrs):
        "处理自己结束的标签，如< img />"
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)
    def handle_starttag(self, tag, attrs):
        "处理开始标签，比如< div>；这里的attrs获取到的是属性列表，属性以元组的方式展示"
        attrs = {k:v for k,v in attrs}
        tag = HtmlTag(tag, attrs)
        self.stacks[-1].add_node(tag)
        self.stacks.append(tag)
    def handle_data(self, data):
        self.stacks[-1].add_text(data)
        "处理数据，标签之间的文本"
    def handle_endtag(self, tag):
        self.stacks.pop(-1)
        "处理结束标签,比如< /div>"

pass
def is_node(node):
    return isinstance(node, HtmlTag)
is_tag = is_node
def parse(text):
    text=text.replace("\r", "").replace("\n", "")
    obj = MyHTMLParser()
    obj.feed(text)
    return obj.data

pass

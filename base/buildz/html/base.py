from html.parser import HTMLParser
from .. import xf
from ..base import Base
import re
__all__ = "HtmlTag,is_node,is_tag,parse,wrap,xwrap,w,xw,r,xr,x2j".split(",")
def wrap(tag, s):
    return f"<{tag}>{s}</{tag}>"
def xwrap(**kv):
    rst = [f"<{k}>{v}</{k}>" for k,v in kv.items()]
    return "".join(rst)
w=wrap
xw=xwrap
r=w
xr=xw
def arr(obj, keys, key):
    arr = obj.tags(keys)
    if len(arr)==1:
        arr = arr[0].tags(key)
    else:
        arr = []
    return arr
def x2j(node):
    if isinstance(node, HtmlTag):
       node = node.simple()
    return node
class HtmlTag:
    def simple(self):
        if self.text:
            return self.text
        rst = {}
        for k,v in self.maps.items():
            rst[k] = v[0].simple()
        return rst
    def data(self):
        return self.to_maps()
    def to_maps(self):
        nodes = [n.to_maps() if is_node(n) else str(n) for n in self.nodes]
        rst = {'tag': self.tag, 'attrs': self.attrs, 'nodes': nodes}
        return rst
    def __str__(self):
        return xf.dumps(self.to_maps())
    def __repr__(self):
        return self.__str__()
    def get_tags(self, name):
        return self.maps.get(name, [])
    def tags(self, tag, depth=1):
        rst=[]
        if depth>0:
            depth-=1
        for nd in self.nodes:
            if not is_node(nd):
                continue
            if nd.tag==tag:
                rst.append(nd)
            if depth!=0:
                rst+=nd.tags(tag, depth)
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
def parse(text, keep_enter=False):
    text=text.replace("\r", "")
    if not keep_enter:
        text = text.replace("\n", "")
    obj = MyHTMLParser()
    obj.feed(text)
    return obj.data

pass

from html.parser import HTMLParser
from .. import xf
import re
class HtmlTag:
    def to_maps(self):
        nodes = [n.to_maps() for n in self.nodes]
        rst = {'tag': self.tag, 'attrs': self.attrs, 'texts': self.texts, 'text': self.text, 'childs': nodes}
        return rst
    def __str__(self):
        return xf.dumps(self.to_maps())
    def __repr__(self):
        return self.__str__()
    def match(self, val, pt):
        if type(pt)==list:
            tp = pt[0]
            v = pt[1]
        else:
            tp = "="
            v = pt
        if tp == '>':
            return val>v
        elif tp == "<":
            return val<v
        elif tp == "=":
            return val == v
        elif tp == ">=":
            return val>=v
        elif tp=="<=":
            return val<=v
        elif tp == "re":
            return (re.findall(v, val))>0
        elif tp == 'sh':
            #v.replace("${it}", val)
            return eval(v)
        else:
            raise Exception(f"not impl match type: '{tp}'")
    def check(self, maps):
        #print(f"[TESTZ] check: {maps}, attrs: {self.attrs}")
        for k,v in maps.items():
            if k == 'tag':
                if not self.match(self.tag, v):
                    return False
            elif k == "$":
                return self.match(None, ["sh", v])
            else:
                if k not in self.attrs or not self.match(self.attrs[k], v):
                    return False
        return True
    def __init__(self, tag, attrs=None):
        self.tag = tag
        if attrs is None:
            attrs = {}
        self.attrs = attrs
        self.nodes = []
        self.text = None
        self.texts = []
    def _search(self, rst, maps):
        if self.check(maps):
            rst.append(self)
        for n in self.nodes:
            n._search(rst, maps)
    def searchs(self, **maps):
        rst = []
        self._search(rst, maps)
        return rst
    def tags(self, _tag):
        return self.searchs(tag = _tag)
    def finds(self, s):
        rst = []
        maps = xf.loads(s)
        self._search(rst, maps)
        return rst
    def add_node(self, node):
        self.nodes.append(node)
    def add_text(self, text):
        self.text = text
        self.texts.append(text)

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
        pass
    def handle_starttag(self, tag, attrs):
        "处理开始标签，比如< div>；这里的attrs获取到的是属性列表，属性以元组的方式展示"
        attrs = {k:v for k,v in attrs}
        tag = HtmlTag(tag, attrs)
        self.stacks[-1].add_node(tag)
        self.stacks.append(tag)
        #print(f"Encountered a {tag} start tag")
        #for attr, value in attrs:
        #    print(f"   {attr} = {value}")
    def handle_data(self, data):
        self.stacks[-1].add_text(data)
        "处理数据，标签之间的文本"
        #print(f"----handle data in tags: {data}")
    def handle_endtag(self, tag):
        self.stacks.pop(-1)
        "处理结束标签,比如< /div>"
        #print(f"Encountered a {tag} end tag")

pass

def parse(text):
    obj = MyHTMLParser()
    obj.feed(text)
    return obj.data

pass
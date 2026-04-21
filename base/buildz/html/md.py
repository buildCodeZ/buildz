
from .base import is_node, parse
from buildz.base import Base
import re
__all__ = "dumps,dump,dump_html,MDTree,load".split(",")
def match(pt, s):
    return len(re.findall(pt, s))>0
def dumps(nodes, conf={}, strip=False):
    rst = [dump(nd, conf) for nd in nodes]
    rs = "".join(rst)
    if strip:
        rs = rs.strip()
    return rs
def dump(node, conf={}):
    if not is_node(node):
        return str(node)
    if node.tag in {"script", "style"}:
        return ""
    content = ""
    tag = node.tag
    if tag[0]=="h" and match("^\d+$", tag[1:]):
        i = int(tag[1:])
        content+=f"{'#'*i} "+dumps(node.nodes, conf, 1)+"\n\n"
    elif tag=='p':
        content+=dumps(node.nodes, conf)+"\n\n"
    elif tag == 'ul' or tag == 'ol':
        if 'list' not in conf:
            conf['list'] = []
        conf['list'].append([tag, 1])
        content += "\n\n"+dumps(node.nodes, conf)
        conf['list'].pop(-1)
    elif tag == 'li':
        lst = conf.get('list', None)
        if not lst or len(lst)==0:
            return ""
        lst=lst[-1]
        if lst[0] == 'ol':
            content += f"{lst[1]}. "
            lst[1]+=1
        else:
            content += "- "
        content+=dumps(node.nodes, conf)+"\n\n"
    elif tag == 'a':
        href = node.get('href')
        if not href:
            return ""
        text = dumps(node.nodes, conf, 1).strip()
        if text != "" and text.find("\n")<0:
            text = f"[{text}]"
        content+=f"{text}({href})"
    elif tag == 'img':
        src = node.get('src')
        if not src:
            return ""
        alt = node.get("alt", "")
        if alt:
            content+=f"![{alt}]({src})"
        else:
            content+=f"![]({src})"
    elif tag in {'strong', 'b'}: 
        content+=f"**{dumps(node.nodes, conf)}**"
    elif tag in {'em', 'i'}:
        content+=f"*{dumps(node.nodes, conf)}*"
    elif tag == 'br':
        content+="\n\n"
    elif tag == 'head':
        content += f"# {dumps(node.nodes, conf)}\n\n"
    else:
        content += dumps(node.nodes,conf)
    return content 
def dump_html(html):
    if not is_node(html):
        html = parse(html)
    content = dump(html)
    return content

def is_title(s):
    if s[:4]=='    ':
        return False
    return match("^#+ +.+", s.strip())

class MDTree(Base):
    @property
    def val(self):
        return self.value
    def str(self):
        data = {'name': self.name, 'value': self.value, 'subs': self.subs}
        return str(data)
    def get_val(self, *a, **b):
        obj = self.get_one(*a, **b)
        if self.is_node(obj):
            obj = obj.val
        return obj
    def gets(self, *a, **b):
        data = self.get(*a, **b)
        if type(data)!=list:
            data = [data]
        return data
    def get_one(self, *a, **b):
        data = self.get(*a, **b)
        if type(data)==list:
            data = data[0]
        return data
    def get(self, *a, **b):
        return self.subs.get(*a, **b)
    def __getitem__(self, key):
        return self.subs[key]
    @staticmethod
    def is_node(node):
        return isinstance(node, MDTree)
    def __init__(self, level, name=None):
        self.name = name
        self.level = level
        self.datas = []
        self.subs = {}
        self.value = ""
    def add(self, data):
        self.datas.append(data)
        if self.is_node(data):
            name = data.name
            if name in self.subs:
                x = self.subs[name]
                if type(x)!=list:
                    self.subs[name] = [x]
                self.subs[name].append(data)
            else:
                self.subs[name] = data
        else:
            data = data.strip("\r")
            if self.value:
                self.value = self.value+"\n"+data
            else:
                self.value = data

pass


def load(content):
    arr = content.split("\n")
    stacks = []
    stacks.append(MDTree(0))
    mark_js = False
    for i in range(len(arr)):
        data = arr[i]
        if data[:4]=='    ':
            stacks[-1].add(data)
            continue
        if data.strip()[:3]=='```':
            stacks[-1].add(data)
            mark_js = not mark_js
            continue
        if mark_js:
            stacks[-1].add(data)
            continue
        if not is_title(data):
            stacks[-1].add(data)
            continue
        data = data.strip()
        tmp = data.split(" ")
        level = len(tmp[0].strip())
        name = " ".join(tmp[1:])
        name = name.strip()
        curr = MDTree(level, name)
        while curr.level<=stacks[-1].level:
            stacks.pop(-1)
        stacks[-1].add(curr)
        stacks.append(curr)
    return stacks[0]





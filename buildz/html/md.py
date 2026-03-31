
from .base import is_node, parse
import re
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

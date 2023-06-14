# Builtins
import re
from typing import Tuple, List
from dataclasses import dataclass
from typing import List, Callable, Tuple, Optional

# External
from markupsafe import escape
from flask import url_for

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    txt = re.sub(r'<br>', ' ', text)
    return TAG_RE.sub('', txt)

def link_from_tag(tag: re.Match) -> str:
    try:
        match = re.findall(r'\[(\S+)\]|\((\S+)\)', tag.group())
        text = match[0][0]
        link = match[1][1]
        html = f'<a class="textlink" href="{link}">{text}</a>'
        return html
    except KeyError as e:
        return tag.group()

def font_mod(text: re.Match) -> str:
    _text = text.group()
    # Hnusný řešení, ale rychlejší než další regex
    if '**' in _text:
        return f"<b>{_text[2:-2]}</b>"
    elif '//' in _text:
        return f"<i>{_text[2:-2]}</i>"
    elif '__' in _text:
        return f"<u>{_text[2:-2]}</u>"
    elif '~~' in _text:
        return f"<del>{_text[2:-2]}</del>"
    elif '^^' in _text:
        return f"<sup>{_text[2:-2]}</sup>"
    elif ',,' in _text:
        return f"<sub>{_text[2:-2]}</sub>"
    else:
        return _text

def heading(text: re.Match) -> str:
    _text = text.group()
    level = _text.count('#')
    if level == 0:
        return _text
    title = _text.replace('#', '').strip()
    return f"<h{level}>{title}</h{level}>"

def index(text: re.Match) -> str:
    _text = text.group()
    return ""

#TODO: code block
#TODO: thread link

                                                    # Vypnout formatovani: @@text@@
tagparsers = {
    r"\[\S+\]\(http(s?)://\S+\)": link_from_tag,    # Odkaz: [text](link)
    r"\*{2}.+\*{2}": font_mod,                      # Tucne: **text**
    r"/{2}.+/{2}": font_mod,                        # Kurziva: //text//
    r"_{2}.+_{2}": font_mod,                        # Podtrzeno: __text__
    r"~{2}.+~{2}": font_mod,                        # Preskrtnuto: ~~text~~
    r"^#{1,3}\s?[^#\n]+$": heading,                 # Titulek/podtitulek: # Text
    r"\^{2}\S+\^{2}": font_mod,                     # Horni index: ^^text^^
    r",{2}\S+,{2}": font_mod,                       # Dolni index: ,,text,,
}

def parse_comment_string(text: str) -> str:

    newtext = list()

    for l in text.split('\r\n'):
        if l.startswith('@@') and l.endswith('@@'):
            newtext.append(l[2:-2])
            continue
        for tag in tagparsers.items():
            l = re.sub(*tag, l, re.IGNORECASE | re.UNICODE)
        newtext.append(l)

    return '<br>'.join(newtext)
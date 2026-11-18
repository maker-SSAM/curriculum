"""NCIC 본문 html(.boardViewContent)을 줄 단위 글자로 바꾼다. 다른 도구에서 불러 쓴다."""
from html.parser import HTMLParser
import re

BLOCK = {"p", "div", "tr", "li", "br", "h1", "h2", "h3", "h4", "table"}
CELL = {"td", "th"}


class _P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0  # boardViewContent 안쪽 깊이
        self.buf = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.depth == 0:
            if tag == "div" and "boardViewContent" in (a.get("class") or ""):
                self.depth = 1
            return
        if tag == "div":
            self.depth += 1
        if tag in ("script", "style"):
            self.skip += 1
        if tag in BLOCK:
            self.buf.append("\n")
        elif tag in CELL:
            self.buf.append("\n\t")

    def handle_endtag(self, tag):
        if self.depth == 0:
            return
        if tag in ("script", "style"):
            self.skip -= 1
        if tag in BLOCK or tag in CELL:
            self.buf.append("\n")
        if tag == "div":
            self.depth -= 1

    def handle_data(self, data):
        if self.depth and not self.skip:
            self.buf.append(data)


def lines(html: str):
    p = _P()
    p.feed(html)
    text = "".join(p.buf).replace("\xa0", " ")
    out = []
    for ln in text.split("\n"):
        ln = re.sub(r"[ \t\r]+", " ", ln).strip()
        if ln:
            out.append(ln)
    return out

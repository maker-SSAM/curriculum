"""NCIC 원문 인벤토리 웹 본문(2022 개정 초등 수학)을 받아 원문/ncic-web/ 에 html로 저장한다.

python tools/fetch_ncic.py
"""
import http.cookiejar
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://ncic.re.kr"
LOC = "2022 개정 시기 > 초등학교(2022.12) > 수학 > 2. 내용 체계 및 성취기준"
PAGES = {
    "10069374": ("내용체계", LOC),
    "10069376": ("1-2학년", LOC + " > 나. 성취기준"),
    "10069377": ("3-4학년", LOC + " > 나. 성취기준"),
    "10069378": ("5-6학년", LOC + " > 나. 성취기준"),
}

out = Path(__file__).resolve().parent.parent / "원문" / "ncic-web"
out.mkdir(parents=True, exist_ok=True)

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
op.addheaders = [("User-Agent", "Mozilla/5.0")]

html = op.open(BASE + "/inv/org/list.do", timeout=30).read().decode("utf-8")
m = re.search(r'name="_csrf"\s+value="([^"]+)"', html) or re.search(r'value="([^"]+)"\s+name="_csrf"', html)
if not m:
    sys.exit("_csrf 값을 찾지 못함")
csrf = m.group(1)

for seq, (name, loc) in PAGES.items():
    body = urllib.parse.urlencode({
        "_csrf": csrf, "openYear": "2022", "seq": seq, "location": loc,
        "orgType": "ogi4", "menuType": "1", "nationCd": "",
    }).encode()
    page = op.open(BASE + "/inv/org/view.do", data=body, timeout=30).read().decode("utf-8")
    if "boardViewContent" not in page:
        sys.exit(f"{name}: 본문이 없음")
    (out / f"{name}.html").write_text(page, encoding="utf-8", newline="\n")
    print(name, len(page))

"""공식 HWPX에서 '공통 교육과정 > 수학'의 원문을 순서대로 뽑는다(초등 범위).

넣는 것: 교육과정 설계의 개요(그림 포함), 1. 성격 및 목표, 2. 가. 내용 체계(표의 초등 칸만),
        3. 교수·학습 및 평가.
'나. 성취기준'은 자리만 남긴다(대조를 마친 data/초등수학_성취기준.json을 웹에서 그 자리에 보여 줌).
PDF에서는 문단마다 '이 글이 PDF에 있는가'를 본다(수식 기호는 빼고).

python -E -P -X utf8 tools/extract_wonmun.py → data/원문_수학_초등.json, img/overview.png
"""
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract import EQ, HWPX, ROOT, norm, pdf_blob  # noqa: E402

KEEP_COLS = 4  # 내용 체계 표: 0=범주, 1~3=초등 1~2·3~4·5~6학년 (4~6=중학교는 뺌)


def tag(el):
    return el.tag.split("}")[1]


def walk_p(p, out, pics):
    """문단 하나 → 블록들. 글자는 모으고, 표·그림·글상자는 따로 낸다."""
    buf = []

    def flush():
        t = re.sub(r"[ \t]+", " ", "".join(buf)).strip()
        if t:
            out.append({"t": "p", "text": t})
        buf.clear()

    for run in p:
        if tag(run) != "run":
            continue
        for el in run:
            k = tag(el)
            if k == "t":
                buf.append("".join(el.itertext()))
            elif k == "equation":
                s = "".join(x.text or "" for x in el if tag(x) == "script").strip()
                buf.append(EQ.get(s, "{수식:" + s + "}"))
            elif k == "tbl":
                flush()
                walk_tbl(el, out, pics)
            elif k == "pic":
                flush()
                ref = next((x.get("binaryItemIDRef") for x in el.iter() if x.get("binaryItemIDRef")), None)
                out.append({"t": "img", "ref": ref})
                pics.append(ref)
            elif k in ("rect", "ellipse", "container"):
                flush()
                for sub in el.iter():
                    if tag(sub) == "subList":
                        for q in sub:
                            if tag(q) == "p":
                                walk_p(q, out, pics)
    flush()


def walk_tbl(tbl, out, pics):
    rows, cols = int(tbl.get("rowCnt")), int(tbl.get("colCnt"))
    cells = []
    for tc in tbl.iter():
        if tag(tc) != "tc":
            continue
        addr = next(x for x in tc if tag(x) == "cellAddr")
        span = next(x for x in tc if tag(x) == "cellSpan")
        paras = []
        for sub in tc:
            if tag(sub) == "subList":
                for q in sub:
                    if tag(q) == "p":
                        blocks = []
                        walk_p(q, blocks, pics)
                        paras += [b["text"] for b in blocks if b["t"] == "p"]
        cells.append({"r": int(addr.get("rowAddr")), "c": int(addr.get("colAddr")),
                      "rs": int(span.get("rowSpan")), "cs": int(span.get("colSpan")), "lines": paras})
    if rows * cols == 1 or len(cells) == 1:  # 글상자처럼 쓰인 한 칸짜리 표 → 문단으로
        for ln in cells[0]["lines"] if cells else []:
            out.append({"t": "p", "text": ln})
        return
    out.append({"t": "table", "rows": rows, "cols": cols, "cells": cells})


def blocks_all():
    z = zipfile.ZipFile(HWPX)
    root = ET.fromstring(z.read("Contents/section0.xml"))
    out, pics = [], []
    for p in root:
        if tag(p) == "p":
            walk_p(p, out, pics)
    return out, z


def cut(blocks):
    """공통 교육과정 '수학'의 설계 개요 ~ 평가 끝. 성취기준(초·중)은 자리표로 바꾼다."""
    texts = [b.get("text", "") for b in blocks]
    start = next(i for i, t in enumerate(texts) if t == "교육과정 설계의 개요")
    end = next(i for i in range(start + 1, len(texts)) if texts[i] == "선택 중심 교육과정")
    ach = next(i for i in range(start, end) if texts[i] == "나. 성취기준")
    teach = next(i for i in range(ach, end) if texts[i].startswith("3. 교수"))
    return blocks[start:ach + 1] + [{"t": "standards"}] + blocks[teach:end]


def elementary_only(tb):
    cells = []
    for c in tb["cells"]:
        if c["c"] >= KEEP_COLS:
            continue
        c = dict(c, cs=min(c["cs"], KEEP_COLS - c["c"]))
        cells.append(c)
    return dict(tb, cols=KEEP_COLS, cells=cells)


def kind(text):
    """문단 모양: 제목 단계와 들여쓰기."""
    if re.match(r"^\(\d+\) ", text):  # 짧으면 소제목((1) 수와 연산), 길면 목록((1) 수학적 지식을 …)
        return "h4" if len(text) <= 25 else "l1"
    pats = [(r"^\d+\. ", "h2"), (r"^[가-하]\. ", "h3"), (r"^\([가-하]\) ", "l1"),
            (r"^[①-⑳]", "l2"), (r"^[㉠-㉻]", "l3"), (r"^⋅", "dot"), (r"^\[.*\]$", "caption")]
    for pat, k in pats:
        if re.match(pat, text):
            return k
    return "p"


def main():
    blocks, z = blocks_all()
    part = cut(blocks)
    imgdir = ROOT / "img"
    imgdir.mkdir(parents=True, exist_ok=True)
    res, missing = [], []
    blob = pdf_blob(range(0, 60))
    for b in part:
        if b["t"] == "p":
            if b["text"] in ("교육과정 설계의 개요",):
                b = dict(b, k="h2")
            else:
                b = dict(b, k=kind(b["text"]))
            if norm(b["text"], True) and norm(b["text"], True) not in blob:
                missing.append(b["text"])
        elif b["t"] == "table":
            b = elementary_only(b)
            for c in b["cells"]:
                for ln in c["lines"]:
                    if norm(ln, True) and norm(ln, True) not in blob:
                        missing.append(ln)
        elif b["t"] == "img":
            name = [n for n in z.namelist() if n.startswith(f"BinData/{b['ref']}.")][0]
            from PIL import Image  # BMP → PNG
            import io
            im = Image.open(io.BytesIO(z.read(name))).convert("RGB")
            im.save(imgdir / "overview.png", optimize=True)
            b = {"t": "img", "src": "img/overview.png", "w": im.width, "h": im.height,
                 "alt": "수학과 교육과정 설계의 개요 그림: 가운데 핵심 아이디어를 지식·이해, 과정·기능, 가치·태도가 둘러싸고, "
                        "그 바깥에 네 영역(수와 연산, 변화와 관계, 도형과 측정, 자료와 가능성), 다시 그 바깥에 다섯 교과 역량"
                        "(문제해결, 추론, 의사소통, 연결, 정보처리)이 있으며, 가장 바깥에 수학 교과 역량 함양, 학생 주도성 강화, "
                        "학생 맞춤형 지도, 공학 도구 활용, 온라인 교육환경 활용이 놓인 원 그림"}
        res.append(b)
    out = ROOT / "data" / "원문_수학_초등.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    n = {k: sum(1 for b in res if b["t"] == k) for k in ("p", "table", "img", "standards")}
    print(f"{out.relative_to(ROOT)}: {n}")
    print(f"PDF에서 못 찾은 글 {len(missing)}줄")
    for m in missing:
        print("  -", m[:120])


if __name__ == "__main__":
    main()

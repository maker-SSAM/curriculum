"""2022 개정 초등 수학 성취기준을 세 출처에서 뽑아 서로 맞춰 본다.

  A    원문/ncic-web/*.html      NCIC 원문 인벤토리 웹 본문 (먼저 tools/fetch_ncic.py)
  HWPX 원문/[별책8] 수학과 교육과정.hwpx  (선생님이 HWP에서 바꿈. 수식 기호를 살려 읽음)
  PDF  원문/[별책8] 수학과 교육과정.pdf   (17~38쪽. 줄바꿈·띄어쓰기·수식 기호가 흐트러져 있어 글자만 대조)

python -E -P -X utf8 tools/extract.py  →  data/초등수학_원본추출.json (출처별), data/대조_차이목록.json
"""
import json
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from htmltext import lines as html_lines  # noqa: E402

SRC = ROOT / "원문"
HWPX = SRC / "[별책8] 수학과 교육과정.hwpx"
PDF = SRC / "[별책8] 수학과 교육과정.pdf"
BANDS = {"2": "1~2학년", "4": "3~4학년", "6": "5~6학년"}

CODE = re.compile(r"^[•·]?\s*\[(\d)수(\d\d)-(\d\d)\]\s*(.*)$")
AREA = re.compile(r"^\((\d)\)\s*(\S.*)$")
BAND = re.compile(r"^\[(초등학교|중학교)\s*(\d)\s*[∼~～-]\s*(\d)학년\]")
# 소주제 앞 번호: 웹은 Ⅰ. / Ⅰ / Ⅳ, , 공식본은 사용자 영역 글자(동그라미 숫자)·한글 호환 글자
SUBNUM = re.compile(r"^([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]+[.,]?|[-\U000F0000-\U000FFFFD]|[숔숕숖숗수숙숚숛순숝숞숟]|[①-⑳])\s*")

EQ = {"times": "×", "div": "÷", "TIMES": "×", "DIV": "÷", "-": "-", "+": "+", "=": "=",
      "<": "<", ">": ">", "LEQ": "≤", "GEQ": "≥", "leq": "≤", "geq": "≥", "cdot": "·"}


def parse(lines, src):
    """줄 목록 → {code: {...}}, {(band, area): {...}}"""
    stds, secs, band = {}, {}, None
    area = sub = None
    mode = "std"
    last_exp = None
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        m = BAND.match(ln)
        if m:
            band = m.group(3) if m.group(1) == "초등학교" else None
            area, mode = None, "std"
            continue
        if band is None:
            continue
        m = AREA.match(ln)
        if m and len(ln) < 20:
            area = m.group(1)
            secs.setdefault((band, area), {"name": m.group(2).strip(), "subtopics": [], "considerations": []})
            mode, sub = "std", None
            continue
        if ln.startswith("(가)"):
            mode = "exp"
            continue
        if ln.startswith("(나)"):
            mode = "con"
            continue
        m = CODE.match(ln)
        if m and mode in ("std", "exp"):
            code = f"[{m.group(1)}수{m.group(2)}-{m.group(3)}]"
            if mode == "std":
                if code in stds:
                    print(f"  ! {src}: {code} 두 번 나옴", file=sys.stderr)
                stds[code] = {"code": code, "band": m.group(1), "area": m.group(2), "subtopic": sub,
                              "text": m.group(4).strip(), "explanation": []}
            else:
                stds.setdefault(code, {"code": code, "explanation": []})["explanation"].append(m.group(4).strip())
                last_exp = code
            continue
        sec = secs.get((band, area))
        if sec is None:
            continue
        if mode == "std":
            sub = SUBNUM.sub("", ln).strip()
            sec["subtopics"].append(sub)
        elif mode == "exp":
            if last_exp:
                stds[last_exp]["explanation"].append(ln.lstrip("•· ").strip())
        else:
            sec["considerations"].append(ln.lstrip("•· ").strip())
    return stds, secs


def web_lines():
    out = []
    for f in ("1-2학년", "3-4학년", "5-6학년"):
        out.append(f"[초등학교 {f[0]}~{f[2]}학년]")  # 1~2, 5~6 쪽은 본문에 학년군 제목이 없음
        out += html_lines((SRC / "ncic-web" / f"{f}.html").read_text(encoding="utf-8"))
    out.append("[중학교 1~3학년]")
    return out


def hwpx_lines():
    root = ET.fromstring(zipfile.ZipFile(HWPX).read("Contents/section0.xml"))
    out = []
    for p in root.iter():
        if not p.tag.endswith("}p"):
            continue
        buf = []
        for run in p:
            if not run.tag.endswith("}run"):
                continue
            for el in run:
                tag = el.tag.split("}")[1]
                if tag == "t":
                    buf.append("".join(el.itertext()))
                elif tag == "equation":
                    s = "".join(x.text or "" for x in el if x.tag.endswith("}script")).strip()
                    buf.append(EQ.get(s, "{수식:" + s + "}"))
        t = "".join(buf).strip()
        if t:
            out.append(t)
    return out


def pdf_blob(pages=range(16, 38)):
    """PDF 17~38쪽 글자를 한 줄로(띄어쓰기·수식 기호 뺌). pypdf가 몇 쪽은 글상자 순서를 뒤섞어 읽으므로
    구조로 나누지 않고 '이 문장이 PDF 안에 있는가'만 본다."""
    from pypdf import PdfReader
    r = PdfReader(str(PDF))
    raw = []
    for i in pages:  # 기본 17~38쪽
        for ln in (r.pages[i].extract_text() or "").split("\n"):
            s = ln.strip()
            if s in ("공통 교육과정", "수학과 교육과정") or re.fullmatch(r"\d{1,3}", s):
                continue
            raw.append(s.lstrip("•").strip())
    return norm("".join(raw), True)


def norm(s, drop_symbols=False):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("∼", "~").replace("～", "~").replace("−", "-").replace("–", "-")
    s = re.sub(r"\s+", "", s)
    if drop_symbols:
        s = re.sub(r"\{수식:[^}]*\}", "", s)
        s = re.sub(r"[+\-×÷=<>()（）·]", "", s)
    return s

def ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def pick(a, h, where, fixes):
    """A(웹) 글을 쓰되, 띄어쓰기만 다르면 공식본(HWPX)을 따른다. 공식본이 수식(분수 등)이면 A를 둔다."""
    a, h = ws(a), ws(h)
    if a == h or h is None or "{수식:" in h:
        return a
    if norm(a) == norm(h):
        fixes.append({"where": where, "A": a, "고친 글": h, "까닭": "띄어쓰기를 공식본(HWPX)대로"})
        return h
    fixes.append({"where": where, "A": a, "HWPX": h, "까닭": "글이 달라 A를 그대로 둠 — 확인 필요"})
    return a


def build(A, H):
    fixes = []
    bands = []
    for b, bname in BANDS.items():
        areas = []
        for (bb, an), sec in sorted(A[1].items()):
            if bb != b:
                continue
            hsec = H[1][(bb, an)]
            subs = []
            for i, title in enumerate(sec["subtopics"], 1):
                title = pick(title, hsec["subtopics"][i - 1], f"{bname} 영역{an} 소주제{i}", fixes)
                subs.append({"no": i, "title": title, "standards": []})
            for code, st in sorted(A[0].items()):
                if st.get("band") != b or int(st.get("area", 0)) != int(an):
                    continue
                hs = H[0][code]
                idx = sec["subtopics"].index(st["subtopic"])
                subs[idx]["standards"].append({
                    "code": code,
                    "text": pick(st["text"], hs["text"], code, fixes),
                    "explanation": [pick(x, y, code + " 해설", fixes)
                                    for x, y in zip(st["explanation"], hs["explanation"])],
                })
            areas.append({
                "no": int(an), "name": ws(sec["name"]), "subtopics": subs,
                "considerations": [pick(x, y, f"{bname} 영역{an} 고려 사항", fixes)
                                   for x, y in zip(sec["considerations"], hsec["considerations"])],
            })
        bands.append({"band": bname, "codePrefix": b, "areas": areas})
    data = {
        "title": "2022 개정 교육과정 초등학교 수학 성취기준",
        "source": {
            "고시": "교육부 고시 제2022-33호 [별책 8] 수학과 교육과정 (2022.12.22.)",
            "본문": "NCIC 국가교육과정정보센터 원문 인벤토리 웹 본문 (https://ncic.re.kr)",
            "대조": "NCIC 원문 및 해설서의 [별책8] 수학과 교육과정 HWPX(HWP에서 변환)·PDF",
            "뽑은 날": "2026-11-18",
            "범위": "초등학교 1~6학년(성취기준·해설·적용 시 고려 사항). 내용 체계 표는 넣지 않음",
        },
        "bands": bands,
    }
    return data, fixes


def main():
    A = parse(web_lines(), "A")
    H = parse(hwpx_lines(), "HWPX")
    for k, (stds, secs) in (("A", A), ("HWPX", H)):
        per = {BANDS[b]: sum(1 for s in stds.values() if s.get("band") == b) for b in BANDS}
        print(f"{k}: 성취기준 {len(stds)}개 {per}, 학년군·영역 묶음 {len(secs)}개")
    try:
        blob = pdf_blob()
    except ImportError:
        blob = None
        print("pypdf가 없어 PDF 대조는 건너뜀", file=sys.stderr)

    report = []

    def add(kind, where, a, h):
        report.append({"kind": kind, "where": where, "A": a, "HWPX": h})

    def in_pdf(kind, where, text):
        if blob is not None and text and norm(text, True) not in blob:
            report.append({"kind": "PDF에서 못 찾음:" + kind, "where": where, "A": text})

    for c in sorted(set(A[0]) | set(H[0])):
        a, h = A[0].get(c), H[0].get(c)
        if not a or not h or "text" not in a or "text" not in h:
            add("성취기준 빠짐", c, bool(a and "text" in a), bool(h and "text" in h))
            continue
        for fld, name in (("text", "성취기준 문장"), ("subtopic", "소주제")):
            if norm(a.get(fld) or "") != norm(h.get(fld) or ""):
                add(name, c, a.get(fld), h.get(fld))
        if [norm(x) for x in a["explanation"]] != [norm(x) for x in h["explanation"]]:
            add("성취기준 해설", c, a["explanation"], h["explanation"])
        in_pdf("성취기준 문장", c, a["text"])
        for x in a["explanation"]:
            in_pdf("성취기준 해설", c, x)
    for key in sorted(set(A[1]) | set(H[1])):
        a, h = A[1].get(key), H[1].get(key)
        where = f"{BANDS[key[0]]} 영역{key[1]}"
        if not a or not h:
            add("영역 빠짐", where, bool(a), bool(h))
            continue
        if norm(a["name"]) != norm(h["name"]):
            add("영역 이름", where, a["name"], h["name"])
        if [norm(x) for x in a["subtopics"]] != [norm(x) for x in h["subtopics"]]:
            add("소주제 목록", where, a["subtopics"], h["subtopics"])
        ac, hc = a["considerations"], h["considerations"]
        if len(ac) != len(hc):
            add("고려 사항 개수", where, len(ac), len(hc))
        for i, (x, y) in enumerate(zip(ac, hc)):
            if norm(x) != norm(y):
                add("고려 사항", f"{where} #{i+1}", x, y)
        for i, x in enumerate(ac):
            in_pdf("고려 사항", f"{where} #{i+1}", x)

    out = ROOT / "data"
    out.mkdir(exist_ok=True)
    dump = {k: {"standards": v[0], "sections": {f"{b}-{a}": s for (b, a), s in v[1].items()}}
            for k, v in (("A", A), ("HWPX", H))}
    (out / "초등수학_원본추출.json").write_text(json.dumps(dump, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    (out / "대조_차이목록.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"차이 {len(report)}건 → data/대조_차이목록.json")
    data, fixes = build(A, H)
    n = sum(len(s["standards"]) for b in data["bands"] for a in b["areas"] for s in a["subtopics"])
    (out / "초등수학_성취기준.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    (out / "대조_고친곳.json").write_text(json.dumps(fixes, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"성취기준 {n}개 → data/초등수학_성취기준.json, 고친 곳 {len(fixes)}건 → data/대조_고친곳.json")


if __name__ == "__main__":
    main()

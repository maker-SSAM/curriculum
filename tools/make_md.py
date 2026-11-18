"""data/초등수학_성취기준.json → data/초등수학_성취기준_전문.md

성취기준 문장 + 성취기준 해설(그 성취기준 바로 아래) + 영역별 적용 시 고려 사항.
python -E -P -X utf8 tools/make_md.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "초등수학_성취기준.json"
OUT = ROOT / "data" / "초등수학_성취기준_전문.md"
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮"


def esc(s):
    """마크다운이 기호로 읽지 않게: \\ * _ ` 와, 태그처럼 보이는 < (뒤에 영문·/·!) 앞에 \\ 를 붙인다."""
    s = re.sub(r"([\\*_`])", r"\\\1", s)
    return re.sub(r"<(?=[A-Za-z/!])", r"\\<", s)


def main():
    d = json.loads(SRC.read_text(encoding="utf-8"))
    src = d["source"]
    n = sum(len(s["standards"]) for b in d["bands"] for a in b["areas"] for s in a["subtopics"])
    L = [f"# {d['title']}", ""]
    L.append(f"- 고시: {src['고시']}")
    L.append(f"- 본문: {src['본문']}")
    L.append(f"- 대조: {src['대조']}")
    L.append(f"- 범위: 초등학교 1~6학년, 성취기준 {n}개 · 성취기준 해설 · 적용 시 고려 사항 (내용 체계 표는 없음)")
    L.append(f"- 만든 날: {src['뽑은 날']}")
    L.append("")
    L.append("## 차례")
    for b in d["bands"]:
        cnt = sum(len(s["standards"]) for a in b["areas"] for s in a["subtopics"])
        areas = " · ".join(f"({a['no']}) {a['name']}" for a in b["areas"])
        L.append(f"- [초등학교 {b['band']}](#초등학교-{b['band'].replace('~', '')}) — {cnt}개: {areas}")
    L.append("")
    for b in d["bands"]:
        L += ["---", "", f"## 초등학교 {b['band']}", ""]
        for a in b["areas"]:
            L += [f"### ({a['no']}) {a['name']}", ""]
            for s in a["subtopics"]:
                L += [f"#### {CIRCLED[s['no'] - 1]} {esc(s['title'])}", ""]
                for st in s["standards"]:
                    L.append(f"- **{st['code']}** {esc(st['text'])}")
                    for x in st["explanation"]:
                        L.append(f"  - *해설*: {esc(x)}")
                L.append("")
            L += [f"##### 적용 시 고려 사항 — {b['band']} ({a['no']}) {a['name']}", ""]
            L += [f"- {esc(x)}" for x in a["considerations"]]
            L.append("")
    OUT.write_text("\n".join(L).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT)}: 성취기준 {n}개, {len(L)}줄")


if __name__ == "__main__":
    main()

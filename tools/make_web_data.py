"""웹페이지가 읽을 데이터 묶음을 만든다: assets/data.js

data/초등수학_성취기준.json(대조를 마친 성취기준) + data/원문_수학_초등.json(원문 글)
→ window.CURRICULUM = {...}  (fetch 없이 읽게 해서 파일을 두 번 눌러 열어도 됨)

python -E -P -X utf8 tools/make_web_data.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    std = json.loads((ROOT / "data" / "초등수학_성취기준.json").read_text(encoding="utf-8"))
    won = json.loads((ROOT / "data" / "원문_수학_초등.json").read_text(encoding="utf-8"))
    bundle = {
        "title": std["title"],
        "source": std["source"],
        "files": {
            "pdf": "원문/[별책8] 수학과 교육과정.pdf",
            "hwp": "원문/[별책8] 수학과 교육과정.hwp",
            "hwpx": "원문/[별책8] 수학과 교육과정.hwpx",
            "md": "data/초등수학_성취기준_전문.md",
        },
        "bands": std["bands"],
        "wonmun": won,
    }
    out = ROOT / "assets" / "data.js"
    out.parent.mkdir(exist_ok=True)
    js = "/* tools/make_web_data.py로 만든 파일. 손으로 고치지 않는다. */\nwindow.CURRICULUM = " + \
        json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + ";\n"
    out.write_text(js, encoding="utf-8", newline="\n")
    n = sum(len(s["standards"]) for b in std["bands"] for a in b["areas"] for s in a["subtopics"])
    print(f"{out.relative_to(ROOT)}: 성취기준 {n}개, 원문 블록 {len(won)}개, {out.stat().st_size // 1024}KB")


if __name__ == "__main__":
    main()

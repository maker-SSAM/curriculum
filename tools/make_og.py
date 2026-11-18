"""링크 미리보기 그림 og-image.jpg(1200×630)를 그린다. 숫자는 data/초등수학_성취기준.json에서 센다.

글꼴: 프리텐다드(fonts_OFL/fonts/프리텐다드 또는 korean-ofl-fonts/fonts/pretendard 의 woff2를 임시로 TTF로 바꿔 씀)
필요: pillow, fonttools, brotli
python -E -P -X utf8 tools/make_og.py
"""
import json
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIRS = [ROOT.parent / "fonts_OFL" / "fonts" / "프리텐다드", ROOT.parent / "korean-ofl-fonts" / "fonts" / "pretendard"]
AREA_COLORS = ["#2f6fed", "#0f9d76", "#d9822b", "#a04fd1"]


def font(weight, size, tmp):
    for d in FONT_DIRS:
        src = d / f"Pretendard-{weight}.woff2"
        if src.exists():
            out = Path(tmp) / f"P-{weight}.ttf"
            if not out.exists():
                f = TTFont(str(src))
                f.flavor = None
                f.save(str(out))
            return ImageFont.truetype(str(out), size)
    raise SystemExit("프리텐다드 woff2를 찾지 못함")


def main():
    d = json.loads((ROOT / "data" / "초등수학_성취기준.json").read_text(encoding="utf-8"))
    areas = d["bands"][0]["areas"]
    counts = [sum(len(s["standards"]) for b in d["bands"] for a in b["areas"] if a["no"] == ar["no"] for s in a["subtopics"])
              for ar in areas]
    total = sum(counts)
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#fafaf9")
    g = ImageDraw.Draw(im)
    with tempfile.TemporaryDirectory() as tmp:
        f_lab, f_title = font("SemiBold", 30, tmp), font("ExtraBold", 92, tmp)
        f_sub, f_big = font("Medium", 31, tmp), font("Bold", 30, tmp)
        f_num, f_url = font("ExtraBold", 40, tmp), font("Medium", 26, tmp)
        x = 80
        g.rounded_rectangle((x, 82, x + 470, 132), radius=25, fill="#e8efff")
        g.text((x + 24, 107), "2022 개정 교육과정 · 초등학교 수학", font=f_lab, fill="#2f6fed", anchor="lm")
        g.text((x - 4, 165), "성취기준", font=f_title, fill="#1c1c1e")
        g.text((x - 4, 270), "쉽게보기", font=f_title, fill="#1c1c1e")
        g.text((x, 405), f"성취기준 {total}개를 학년군·영역으로 골라 보고", font=f_sub, fill="#4a4a4f")
        g.text((x, 450), "복사·CSV로 내보내고, 교육과정 원문까지 한곳에서", font=f_sub, fill="#4a4a4f")
        widest = max(g.textlength(t, font=f_sub) for t in ("복사·CSV로 내보내고, 교육과정 원문까지 한곳에서", f"성취기준 {total}개를 학년군·영역으로 골라 보고"))
        g.text((x, 548), "maker-ssam.github.io/curriculum", font=f_url, fill="#8a8a90")

        # 오른쪽: 영역별 막대
        bx, by, bw = 800, 150, 320
        assert x + widest < bx - 30 - 16, f"글이 오른쪽 상자에 닿음: {x + widest:.0f}"
        g.rounded_rectangle((bx - 30, by - 50, bx + bw + 30, by + 4 * 92 + 10), radius=24, fill="#ffffff", outline="#e6e6e3", width=2)
        mx = max(counts)
        for i, (ar, n) in enumerate(zip(areas, counts)):
            y = by + i * 92
            g.text((bx, y - 8), ar["name"], font=f_big, fill="#1c1c1e")
            g.text((bx + bw, y - 8), str(n), font=f_num, fill=AREA_COLORS[i], anchor="ra")
            g.rounded_rectangle((bx, y + 36, bx + bw, y + 50), radius=7, fill="#f0f0ee")
            g.rounded_rectangle((bx, y + 36, bx + max(20, int(bw * n / mx)), y + 50), radius=7, fill=AREA_COLORS[i])
    out = ROOT / "og-image.jpg"
    im.save(out, quality=88, optimize=True, progressive=True)
    print(f"og-image.jpg {out.stat().st_size // 1024}KB, 영역별 {counts}, 합 {total}")


if __name__ == "__main__":
    main()

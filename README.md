# 성취기준 쉽게보기 — 2022 개정 초등 수학

**https://maker-ssam.github.io/curriculum/**

2022 개정 교육과정 초등학교 수학 성취기준 121개를 학년군·영역으로 골라 보고, 낱말로 찾고, 복사·CSV로 내보내고, 교육과정 원문까지 한곳에서 보는 교사용 웹페이지입니다.

- **성취기준**: 학년군·영역 고르기, 검색, 성취기준 해설·적용 시 고려 사항 펼쳐 보기, 고른 것(또는 보이는 것) 복사·CSV 저장, 전문 md 받기
- **한눈에 보기**: 영역 × 학년군 표로 소주제와 성취기준 수
- **교육과정 원문**: 설계의 개요, 성격 및 목표, 내용 체계 표(초등 칸), 성취기준, 교수·학습 및 평가

## 출처와 대조
- 교육부 고시 제2022-33호 [별책 8] 수학과 교육과정(2022.12.22.). 2024.08·2026.01 일부개정에는 수학이 들어 있지 않아 이 문서가 지금 기준입니다.
- 성취기준은 [NCIC 국가교육과정정보센터](https://ncic.re.kr) 원문 인벤토리 웹 본문에서 뽑아, 공식 HWP(HWPX로 변환)·PDF와 한 문장씩 맞춰 보았습니다. 띄어쓰기만 다른 11곳은 공식본대로 고쳤습니다(`data/대조결과.md`).
- 원문 글(설계의 개요·성격 및 목표·내용 체계·교수·학습 및 평가)은 공식 HWPX에서 뽑았고, 모든 문단이 공식 PDF에 있음을 확인했습니다.
- 원문은 바꾸지 않았습니다. 수업·평가 계획에 쓰기 전 공식 문서와 한 번 더 확인해 주세요.

## 폴더
| 폴더 | 내용 |
|---|---|
| `index.html`, `assets/`, `img/` | 웹페이지 (`assets/data.js`는 만들어지는 파일) |
| `data/` | 성취기준 json, 전문 md, 원문 json, 대조 결과 |
| `원문/` | 공식 PDF·HWP·HWPX, NCIC 웹 본문 |
| `tools/` | 받기·뽑기·대조·만들기 도구 |

## 다시 만들기
```bash
python3 tools/fetch_ncic.py      # NCIC 웹 본문 받기
python3 tools/extract.py         # 성취기준 뽑기·대조 (pypdf)
python3 tools/extract_wonmun.py  # 원문 글·그림 뽑기 (pypdf, pillow)
python3 tools/make_md.py         # 전문 md
python3 tools/make_web_data.py   # assets/data.js
python3 tools/make_og.py         # og-image.jpg (pillow, fonttools, brotli)
```
미리보기: `python3 -m http.server 8102` 뒤 http://localhost:8102 (또는 `index.html`을 두 번 눌러 열기)

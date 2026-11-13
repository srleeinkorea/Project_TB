"""공개 문서에 공통 테마(에디토리얼: DM Serif 제목 · DM Sans 본문 · #5170FF)를 넣는다. 여러 번 실행해도 결과가 같다.

사용:
    python 09_도구/sync_theme.py

대상: 01_프로젝트_개요/*.html, 02_회의록/*.html (문서함 첫 화면 프로젝트_현황.html 은 이미 같은 테마라 제외)
하는 일:
  1. </head> 앞에 <style id="tb-theme"> 블록을 넣거나 최신으로 교체함
  2. 그림(SVG)의 글꼴 지정을 Pretendard 로 바꿈
  3. <title> 을 「문서명 · TB 공동연구」 형식으로 맞춤
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"프로젝트_현황.html"}
TARGETS = sorted(ROOT.glob("01_프로젝트_개요/*.html")) + sorted(ROOT.glob("02_회의록/*.html"))

THEME = """<style id="tb-theme">
/* TB 공동연구 문서 테마 v3 (에디토리얼) · 2026-11-13 · 09_도구/sync_theme.py 가 관리함 (직접 수정하지 말 것)
   기준: 비공개_내부검토/261113_TB_흉부질환AI_로드맵_WBS_v1.html 디자인 구조 */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Serif+Display&family=Noto+Sans+KR:wght@400;500;700&display=swap');
:root{
 --tb-sans:'DM Sans','Noto Sans KR',sans-serif;--tb-serif:'DM Serif Display','Noto Sans KR',serif;
 --ink:#0f1222!important;--ink-1:#0f1222!important;--text:#0f1222!important;--navy:#0f1222!important;--brand-dark:#0f1222!important;
 --muted:#4a5068!important;--mute:#7a8094!important;--sub:#4a5068!important;--slate:#7a8094!important;
 --line:#e3e6ef!important;--line-dark:#c9cdd9!important;
 --bg:#fbfbfd!important;--canvas:#fbfbfd!important;--paper:#fff!important;--surface:#fff!important;--panel:#fff!important;
 --blue:#5170FF!important;--brand:#5170FF!important;--accent:#5170FF!important;
 --blue2:#eef1ff!important;--blue-soft:#eef1ff!important;--brand-soft:#eef1ff!important;--tint:#eef1ff!important;
 --green:#1f9d5a!important;--green2:#eaf8f0!important;--green-soft:#eaf8f0!important;
 --amber:#c7861c!important;--amber2:#fff6e6!important;--orange:#c7861c!important;--orange-soft:#fff6e6!important;--warn:#c7861c!important;--warn-soft:#fff6e6!important;
 --red:#e0453f!important;--red2:#fdeeed!important;--danger:#e0453f!important;--danger-soft:#fdeeed!important;
 --grey2:#f0f1f5!important;--slate-soft:#f0f1f5!important
}
html,body{background:#fbfbfd!important}
html{zoom:1.12}  /* 글씨 크기 확대 (2026-11-13) */
body{font-family:var(--tb-sans)!important;color:#0f1222!important;word-break:keep-all}
body *:not(code,pre,kbd,samp,.mono,svg *){font-family:var(--tb-sans)!important}
body :is(h1,h2,.serif,.big,.no,.num,.kpi .n,.lesson-number){font-family:var(--tb-serif)!important;font-weight:400!important;letter-spacing:-.005em!important}
body h1{line-height:1.25!important;color:#0f1222!important}
body h2{line-height:1.35!important}
body h3{font-weight:700!important}
body .no{color:#d9dce6!important}
a{color:#5170FF}
table{border-top:2px solid #0f1222}
table th{background:transparent;color:#4a5068;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;font-weight:700}
:focus-visible{outline:3px solid #a9b8ff;outline-offset:3px}
</style>"""

SVG_FONT = re.compile(r'font-family="(?:DM Sans|DM Serif Display)[^"]*"')


# 문서별 제목 (문서함 메뉴 이름과 맞춤). 새 문서는 여기에 한 줄 추가함
TITLES = {
    "프로젝트_상세현황.html": "프로젝트 상세 현황",
    "결핵_의학_가이드.html": "결핵 의학 가이드",
    "결핵진단_AI_프로젝트_WBS_개요.html": "WBS 개요",
    "251211_추진협의_회의록.html": "회의록 25.12.11 추진 협의",
    "261001_데이터범위협의_회의록.html": "회의록 26.10.01 데이터 범위 협의",
    "261015_추진방향협의_대면_회의록.html": "회의록 26.10.15 추진 방향 협의",
    "2610_온라인협의_회의록.html": "회의록 26.10 온라인 협의",
}


def main():
    for f in TARGETS:
        if f.name in SKIP:
            continue
        t = f.read_text(encoding="utf-8")
        o = t
        t = re.sub(r'\n?<style id="tb-theme">.*?</style>', "", t, flags=re.S)
        t = t.replace("</head>", THEME + "\n</head>", 1)
        t = SVG_FONT.sub('font-family="Pretendard Variable, Pretendard, Malgun Gothic, sans-serif"', t)
        if f.name in TITLES:
            t = re.sub(r"<title>.*?</title>", "<title>" + TITLES[f.name] + " · TB 공동연구</title>", t, count=1, flags=re.S)
        else:
            print("  ※ 제목 미지정: TITLES 에 추가 필요")
        if t != o:
            f.write_text(t, encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", t).group(1)
        print(("갱신 " if t != o else "변경 없음 ") + f.relative_to(ROOT).as_posix() + "  →  " + title)


if __name__ == "__main__":
    main()

"""공개 문서에 공통 테마(서체·색·제목 형식)를 넣는다. 여러 번 실행해도 결과가 같다.

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
/* TB 공동연구 문서 테마 v1 · 2026-11-13 · 09_도구/sync_theme.py 가 관리함 (직접 수정하지 말 것) */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css');
:root{
 --tb-font:'Pretendard Variable',Pretendard,'Malgun Gothic','Apple SD Gothic Neo',system-ui,sans-serif;
 --ink:#1c2940!important;--ink-1:#1c2940!important;--text:#1c2940!important;--navy:#1c2940!important;--brand-dark:#1c2940!important;
 --muted:#53627a!important;--mute:#53627a!important;--sub:#53627a!important;--slate:#6c7890!important;
 --line:#dfe5ef!important;--line-dark:#cbd5e3!important;
 --bg:#f5f7fb!important;--canvas:#f5f7fb!important;--paper:#fff!important;--surface:#fff!important;--panel:#fff!important;
 --blue:#365ee8!important;--brand:#365ee8!important;--accent:#365ee8!important;
 --blue2:#edf2ff!important;--blue-soft:#edf2ff!important;--brand-soft:#edf2ff!important;--tint:#edf2ff!important;
 --green:#177749!important;--green2:#edf8f1!important;--green-soft:#edf8f1!important;
 --amber:#b45309!important;--amber2:#fffbeb!important;--orange:#b45309!important;--orange-soft:#fffbeb!important;--warn:#b45309!important;--warn-soft:#fffbeb!important;
 --red:#b91c1c!important;--red2:#fef2f2!important;--danger:#b91c1c!important;--danger-soft:#fef2f2!important;
 --grey2:#f0f3f9!important;--slate-soft:#f0f3f9!important
}
html,body{background:#f5f7fb!important}
body{font-family:var(--tb-font)!important;color:#1c2940!important;-webkit-font-smoothing:antialiased}
body *:not(code,pre,kbd,samp,.mono,svg *){font-family:var(--tb-font)!important}
body h1{font-weight:800!important;letter-spacing:-.035em!important;line-height:1.35!important;color:#1c2940!important}
body h2{font-weight:750!important;letter-spacing:-.03em!important;line-height:1.45!important}
body h3{font-weight:700!important}
body :is(.big){font-weight:700!important;letter-spacing:-.03em!important;line-height:1.55!important}
body :is(.kpi .n,.no,.num){font-weight:800!important;letter-spacing:-.03em!important}
body .no{color:#cbd5e3!important}
a{color:#365ee8}
table th{background:#f0f3f9;color:#53627a}
:focus-visible{outline:3px solid #93adff;outline-offset:3px}
</style>"""

SVG_FONT = re.compile(r'font-family="(?:DM Sans|DM Serif Display)[^"]*"')


# 문서별 제목 (문서함 메뉴 이름과 맞춤). 새 문서는 여기에 한 줄 추가함
TITLES = {
    "261020_TB_진행상황_원페이지_v1.html": "진행상황 원페이지",
    "TB_프로젝트_소개.html": "프로젝트 소개",
    "결핵_의학_가이드.html": "결핵 의학 가이드",
    "결핵진단_AI_프로젝트_WBS_개요.html": "WBS 개요",
    "251211_추진협의_회의록.html": "회의록 2025.12.11 추진 협의",
    "261001_데이터범위협의_회의록.html": "회의록 2026.10.01 데이터 범위 협의",
    "261015_추진방향협의_대면_회의록.html": "회의록 2026.10.15 추진 방향 협의 (대면)",
    "2610_온라인협의_회의록.html": "회의록 2026.10 온라인 협의",
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

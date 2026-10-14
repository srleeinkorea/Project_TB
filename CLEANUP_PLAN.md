# Project_TB 폴더 정리안 (2026-10-14)

분석 기준: 폴더 전체 약 160MB, 2,000개+ 파일. 이 중 보존 가치가 있는 원본·산출물은 약 15MB / 60개 파일. 나머지는 AI 작업 중간 산출물, 렌더링 캐시, 중복 복사본, node_modules.

**원칙**: 삭제하지 않고 `_to_delete/`로 이동 → 2주간 확인 → 문제없으면 삭제. 아래 명령은 Claude Code에서 실행.

---

## 1. 삭제 대상 (→ `_to_delete/`)

| 분류 | 경로 | 크기 | 사유 |
|------|------|------|------|
| 임시 빌드 | `.tmp_flow_script_v1/` | 9.5MB | pptx 생성 중간물 + node_modules. 최종 pptx는 루트에 있음 |
| 임시 빌드 | `.tmp_drb_one_slide/` | 3.1MB | 위와 동일 |
| 빌드 캐시 | `.build/` | 8.3MB | kickoff_final 렌더 캐시 |
| 분석 캐시 | `.analysis/` | 2.7MB | 슬라이드 PNG 렌더·몽타주. 원본 pptx로 재생성 가능 |
| 패키지 캐시 | `.pnpm-store/` | — | pnpm 캐시 |
| 아카이브 | `tmp/*.tar.gz` (v1~v6) | 6.3MB | WBS 대시보드 배포 아카이브 6개 버전. `tb-wbs-dashboard/`가 원본 |
| 렌더 | `tmp/pdfs/mfds_lung-*.png` | 2.8MB | 식약처 가이드 PDF 페이지 이미지. 원본 PDF는 `working/mfds_ai_lung_cancer_2025.pdf` |
| 렌더 | `working/render_tb_word/` | 3MB | docx 페이지 렌더 15장 |
| 렌더 | `working/render_tb_summary/` | — | 동일 |
| 작업물 | `working/pptx_insert_20260902/` | 1.5MB | pptx 편집 스크립트·템플릿·contact sheet. 결과물은 루트 260903 pptx |
| 작업물 | `working/xlsx_tb_wbs/` | — | WBS xlsx 빌드 스크립트·검증 로그. 결과물은 `outputs/`에 있음 |
| 작업물 | `working/sites-bootstrap/` | — | package.json·lock만 |
| 텍스트 추출 | `working/*.json`, `working/*.txt` (contract_*, research_*, business_plan, regulatory, data_security, meeting_20251211, final_text_check) | 0.5MB | hwp·docx에서 추출한 텍스트 캐시. 원본 문서가 루트에 있음 |
| 검사 캐시 | 루트 `*.inspect.ndjson` 4개 | 0.4MB | pptx 구조 분석 캐시 |
| 검사 캐시 | `outputs/*/…xlsx.inspect.ndjson` | 1.6MB | 동일 |
| 중복 | `OneDrive_2026-08-26/연구 관련 내용 정리/` | 24.5MB | `과제 내용 참고자료/`와 5개 파일 완전 동일 (바이트 단위) |
| 중복 | `OneDrive_2026-08-26/` 루트의 hwp 5개 | 0.4MB | `#최종 계약서 및 사업계획서/`에 최종본 있음. 루트 것은 3월 초안들 |
| 중복 | `OneDrive_2026-08-26/#최종 계약서 및 사업계획서/` 안의 파일 중 Project_TB 루트에 동일 파일이 있는 것 | 1.5MB | 루트에 이미 복사됨 (계획서 6.8/6.9, 계약서, 파기계획서, 인허가 정리, 회의 docx) |
| 코드 | `tb-wbs-dashboard/node_modules/`, `.next/`, `dist/`, `.wrangler/`, `.vinext/`, `.openai/` | 3MB+ | 빌드 산출물. `pnpm install && pnpm build`로 재생성 |
| 기타 | `tools/__pycache__/` | — | |
| 기타 | `wbs-social-preview.png` | 0.7MB | 대시보드 OG 이미지. `tb-wbs-dashboard/public/`에 있어야 할 파일 |

**합계: 약 70MB, 1,900개+ 파일 정리.**

## 2. 보존 — 새 구조로 이동

```
Project_TB/
├── CLAUDE.md
├── README.md                       ← 폴더 안내 (아래 3번 내용)
├── skills/decision-brief/SKILL.md  → .claude/skills/ 로 이동
│
├── 01_계약_계획서/                 ← 확정본만
│   ├── 공동연구개발계약서(안)_마이허브_대한결핵협회_.pdf
│   ├── 공동연구개발계약서(안)_마이허브_대한결핵협회_.hwp
│   ├── 공동연구개발계약서(안)_마이허브_대한결핵협회(2026.6.19)_RA.hwp
│   ├── 대한결핵협회 연구과제 신청서 및 계획서(2026.6.9).pdf / .hwpx
│   ├── 대한결핵협회 연구과제 신청서 및 계획서(2026.6.19)_RA.hwpx
│   ├── 결핵진단 AI 사업계획서.hwp
│   ├── 연구 데이터의 안전성 확보 조치 및 파기 계획서.hwp / .docx
│   ├── 인허가 관련 사항 정리.hwpx
│   └── 이전버전/                   ← 6.8 버전, 초안, 법무검토 버전, SEUM 검토본
│
├── 02_IRB_보안/
│   ├── 1. 기관생명윤리위원회 연구계획서.pdf
│   ├── 2. 기관생명윤리위원회 심의면제 자가점검표.pdf
│   └── 보안과제/                   ← 보안등급 점검표, 보안서약서 (OneDrive에서 이동)
│
├── 03_참고자료/
│   ├── WHO/                        ← CAD_for_TB_screening.pdf, Module 2, TPP, TSS, WHO2025 한글번역
│   ├── 식약처/                     ← mfds_ai_lung_cancer_2025.pdf (working에서 이동)
│   ├── TB_AI_reference 정리.xlsx
│   ├── 결핵_의학_가이드.html
│   └── 참고_대한결핵협회 CXR TB 모델관련 회의_20251211.docx
│
├── 04_회의_보고/                   ← 날짜순 산출물
│   ├── 260828_TB_AI_Kickoff_Meeting_Flow_2026_SRLEE_v2_표본수검토반영.pptx
│   ├── 260903_TB_AI_Kickoff_Meeting_보완본_v2.pptx
│   ├── 260903_TB_AI_Kickoff_Flow_Review_Script_v2.pptx
│   ├── 260903_DRB_필요성_근거_1장.pptx
│   ├── 260826_DRB_심의_및_데이터부족사항_분석.md
│   ├── 260915_Medtech Insight 2026 연계 사전 상담 신청서.hwp
│   ├── 261014_TB_AI_공동연구_추진현황_종합보고.md
│   └── 261015_TB_협회미팅_설득자료_v3.html  (v1·v2는 이전버전/)
│
├── 05_인허가_문서패키지/           ← TB_문서패키지/ 그대로 (index.html, 00~08, document.css)
│
├── 06_WBS/
│   ├── TB_프로젝트_WBS_및_문서승인매트릭스.xlsx  (outputs에서 이동)
│   ├── 결핵진단_AI_프로젝트_WBS_GoogleSites용.html
│   ├── TB_프로젝트_소개.html
│   ├── TB_프로젝트_사업계획_종합정리.docx
│   └── tb-wbs-dashboard/           ← 소스만 (node_modules 등 제외, .gitignore 확인)
│
└── tools/                          ← 유지 (build_tb_summary.py, extract_hwp/hwpx/docx)
```

## 3. 실행 — Claude Code에 붙여넣기

```
Project_TB 폴더를 CLEANUP_PLAN.md 2번 구조대로 정리해줘.
1) 먼저 _to_delete/ 폴더를 만들고 1번 표의 항목을 전부 그리로 이동 (삭제 아님). 이동 전 OneDrive_2026-08-26 중복 파일은 해시로 동일한지 확인하고 다른 파일은 이동하지 말고 보고.
2) 2번 구조대로 폴더를 만들고 파일 이동. 이름은 바꾸지 말 것.
3) skills/decision-brief를 .claude/skills/decision-brief로 이동.
4) tb-wbs-dashboard에 .gitignore가 node_modules/.next/dist/.wrangler를 포함하는지 확인하고 없으면 추가.
5) 완료 후 이동 전/후 파일 수와 용량, 이동하지 못한 파일 목록을 표로 보고. README.md에 최종 폴더 구조를 기록.
```

## 4. 확인 필요 (판단 보류)

- `working/mfds_ai_lung_cancer_2025.pdf` — 식약처 폐암 AI 가이드. 03_참고자료/식약처/로 보존 권장.
- `tmp/pdfs/tb_summary_qa.pdf` — 내용 미확인. 열어보고 판단.
- `outputs/01a0475b-…/` — 세션 ID 폴더명. xlsx만 꺼내고 폴더는 삭제.
- `OneDrive_2026-08-26/` 전체 — 위 이동이 끝나면 빈 폴더가 되므로 삭제.

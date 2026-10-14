# Project_TB — 대한결핵협회 × 마이허브 결핵 AI 공동연구

CXR(흉부 X-ray) 기반 결핵 진단보조 AI 공동연구의 작업 공간. 2026-10-14에 폴더를 재편했다. 원본은 이 폴더 하나이고 GitHub는 백업·공유 사본이다.

## 저장소가 어디에 있나

| 이름 | 위치 | 무엇이 있나 | 누가 보나 |
|---|---|---|---|
| **로컬 원본** | `C:\Users\이사라\Documents\Project_TB` | 전부. 여기서만 고친다 | 나 |
| **GitHub Project_TB** | github.com/srleeinkorea/Project_TB | 공개 산출물·인허가 문서 세트·대시보드·도구. `source/`와 `docs/internal/` 평문은 제외 | 공개 |
| **기밀 문서함** | github.com/srleeinkorea/tb-confidential-63279adc25a7 → srleeinkorea.github.io/tb-confidential-63279adc25a7 | `source/`·`docs/internal/`을 비밀번호로 암호화한 사본. 별도 저장소이며 로컬 `confidential/`가 그 클론. 브라우저에서 복호화 | 비밀번호·주소 아는 사람 |

흐름은 **로컬 원본 → 사본** 한 방향이다.

## 폴더

```
docs/
  briefs/        공개 가능한 HTML 산출물 (프로젝트 소개 · 의학 가이드 · WBS 사이트용)
  regulatory/    KHIDI·DRF·MRS·SDP·RRS·DMP·RMP·SRS·SAP 인허가 문서 세트 (HTML)
  internal/      [git 제외] 내부 검토 산출물: 종합보고 · 협회미팅 설득자료 · DRB 분석 · 킥오프 pptx · WBS xlsx
source/          [git 제외] 받은·보낸 원본
  contracts/     공동연구개발계약서 판본 (hwp·pdf)
  plans/         연구과제 신청서·계획서 · 사업계획서 · 인허가 정리
  irb/           IRB 연구계획서 · 자가점검표 · 데이터 파기 계획서 · 교육 이수증
  security/      보안서약서 · 보안등급 점검표
  meetings/      회의록
  consulting/    KHIDI Medtech Insight 신청서
  references/    WHO TPP · CAD 가이드 등 외부 참고문헌
confidential/    [상위 git 제외, 자체 저장소] 기밀 문서함. manifest.txt(목록) · index.html(로그인 뷰어) · vault/(암호문)
tb-wbs-dashboard/  WBS 대시보드 (Next.js)
tools/           hwp·docx 추출기, 요약 빌더, vault_build.py
working/, tmp/   [git 제외] 작업용
.claude/skills/decision-brief/  의사결정 브리핑 작성 규칙
```

## 규칙

- 산출물은 HTML 단일 파일, 이름은 `YYMMDD_TB_<주제>_v<n>.html`. 수정은 새 버전으로.
- 담당자 실명·협회 내부 판단·계약·IRB가 들어간 문서는 `docs/internal/` 또는 `source/`에 두고, 공개가 필요하면 기밀 문서함으로 올린다.
- 보안서약서·교육 이수증 등 개인 서류는 기밀 문서함에도 올리지 않는다.

## 기밀 문서함 갱신

1. `confidential/manifest.txt`에 `경로 | 제목 | 분류`로 줄을 추가한다.
2. 암호화한다. 비밀번호를 물어본다.
   ```bash
   python tools/vault_build.py
   ```
3. `confidential/` 안에서 커밋·푸시한다 (별도 저장소). 평문은 상위 `.gitignore`로 올라가지 않는다.
   ```bash
   git -C confidential add -A && git -C confidential commit -m "vault 갱신" && git -C confidential push
   ```

암호화는 PBKDF2-SHA256(600,000회) + AES-256-GCM. 비밀번호를 바꾸면 전체를 다시 빌드한다. 비밀번호를 잃으면 복구할 수 없다.

## 로컬에서 보기

```bash
python -m http.server 8787
```
`http://localhost:8787/confidential/` 로 연다. `file://`로는 열리지 않는다(fetch 제한).

## 잠금 문서 (공개 사이트, 비밀번호)

`docs/locked/<이름>/`에는 암호문·params·잠금 뷰어만 둔다. 갱신:
```bash
python tools/lock_doc.py docs/internal/<원본>.html docs/locked/review "제목"
```

'use client';

import { useMemo, useState } from 'react';
import {
  CalendarDays,
  Check,
  ChevronRight,
  ClipboardList,
  FileCheck2,
  Filter,
  Flag,
  Printer,
} from 'lucide-react';

type Status = '완료' | '진행 중' | '예정';
type FilterValue = '전체' | Status;

type Task = {
  id: string;
  task: string;
  period: string;
  start: number;
  end: number;
  output: string;
  owner: string;
  status: Status;
  progress: number;
  phase: string;
};

const months = Array.from({ length: 12 }, (_, index) => index + 1);

const yearInfo: Record<number, { title: string; progress: number; note: string }> = {
  2026: {
    title: '데이터 구축 및 레이블링',
    progress: 7,
    note: '8월 25일 착수 → 범위 정의 → 데이터 선별·익명화 → 전문의 정밀 레이블링',
  },
  2027: {
    title: 'AI 모델 개발 및 성능 검증',
    progress: 0,
    note: '2026년 이월 업무 완료 → 모델 설계·학습 → 단위·통합·시스템 시험',
  },
  2028: {
    title: '식약처 인허가 신청 및 심사 대응',
    progress: 0,
    note: '모델 검증 확정 → 기술문서·임상평가 작성 → 인증 신청 → 보완자료 대응',
  },
  2029: {
    title: '인허가 완료 및 기술이전',
    progress: 0,
    note: '최종 심사 대응 → 승인 → 산출물 이관·운영 교육',
  },
};

const wbs: Record<number, Task[]> = {
  2026: [
    { id: '1.1', task: '과제 착수 및 개발 범위 정의', period: '8월 25일–9월 11일', start: 8, end: 9, output: '개발 의뢰서 (DRF)', owner: '개발사', status: '진행 중', progress: 20, phase: '계획' },
    { id: '1.2', task: '적용 규제·법규 및 요구사항 정의', period: '9월 7–25일', start: 9, end: 9, output: 'RRS · SRS (#12)', owner: '개발사', status: '예정', progress: 0, phase: '입력' },
    { id: '1.3', task: 'IRB·DRB 심의위원회 승인', period: '7–9월', start: 7, end: 9, output: 'IRB·DRB 심의위원회 승인 결과', owner: '협회', status: '진행 중', progress: 67, phase: '입력' },
    { id: '1.4', task: '프리킥오프: 데이터 확보 범위·규모 확정', period: '9월 4일', start: 9, end: 9, output: '데이터 확보 범위·규모 확정 협의록', owner: '공동', status: '예정', progress: 0, phase: '입력' },
    { id: '1.5', task: '임상정보·정답라벨 기준 협의', period: '10월 2주', start: 10, end: 10, output: '프리킥오프 협의록 ②', owner: '공동', status: '예정', progress: 0, phase: '입력' },
    { id: '1.6', task: '데이터 선정·제외 기준 확정', period: '10월 3주', start: 10, end: 10, output: '데이터 수집·선정 기준서 (#18)', owner: '협회', status: '예정', progress: 0, phase: '입력' },
    { id: '1.7', task: '데이터 위험 식별 및 관리 계획', period: '10월 3–4주', start: 10, end: 10, output: 'Risk Management Plan', owner: '개발사', status: '예정', progress: 0, phase: '입력' },
    { id: '1.8', task: 'CXR 데이터 선별 및 품질 점검', period: '10월 4주–11월 2주', start: 10, end: 11, output: '데이터 선별·QC 수행 결과', owner: '협회', status: '예정', progress: 0, phase: '입력' },
    { id: '1.9', task: '레이블링 Tool 개발·기본 시험', period: '9–11월', start: 9, end: 11, output: '레이블링 Tool 배포본', owner: '개발사', status: '예정', progress: 0, phase: '출력' },
    { id: '1.10', task: '데이터 비식별화', period: '11월 2–3주', start: 11, end: 11, output: '익명화 절차서 (#19)', owner: '협회', status: '예정', progress: 0, phase: '입력' },
    { id: '1.11', task: '제주 현장 Tool 설치·교육', period: '11월 2–3주', start: 11, end: 11, output: '현장 방문·I/O 시험 결과', owner: '공동', status: '예정', progress: 0, phase: '입력' },
    { id: '1.12', task: '레이블링 검수·반출 절차 확정', period: '11월 4주', start: 11, end: 11, output: 'Workflow 확정본', owner: '공동', status: '예정', progress: 0, phase: '입력' },
    { id: '1.13', task: '학습용 영상 정밀 레이블링', period: '12월–2027년 2월', start: 12, end: 12, output: '레이블링 기준서·검수 기록 (#20)', owner: '공동', status: '예정', progress: 0, phase: '입력' },
  ],
  2027: [
    { id: '1.14', task: '불일치 Case 재판독·중간 검수', period: '3월 1–2주', start: 3, end: 3, output: '중간 검수·재판독 결과', owner: '공동', status: '예정', progress: 0, phase: '검토' },
    { id: '1.15', task: '참조표준·정답 라벨 최종 확정', period: '3월 3–4주', start: 3, end: 3, output: 'GT 확정 기준서 (#21)', owner: '공동', status: '예정', progress: 0, phase: '검토' },
    { id: '2.1', task: '최종 학습용 데이터셋 인계', period: '3월 4주–4월 1주', start: 3, end: 4, output: '최종 학습용 데이터셋', owner: '공동', status: '예정', progress: 0, phase: '입력' },
    { id: '2.2', task: 'AI 모델 상세 설계', period: '4월', start: 4, end: 4, output: 'SDS · SAD (#7·8)', owner: '개발사', status: '예정', progress: 0, phase: '출력' },
    { id: '2.3', task: '학습환경·오픈소스 구성 관리', period: '5월', start: 5, end: 5, output: 'SBOM (#9·10)', owner: '개발사', status: '예정', progress: 0, phase: '입력' },
    { id: '2.4', task: '1차 모델 학습', period: '6월', start: 6, end: 6, output: '1차 모델 학습 결과', owner: '개발사', status: '예정', progress: 0, phase: '출력' },
    { id: '2.5', task: '교차검증·1차 튜닝', period: '7월', start: 7, end: 7, output: '교차검증·튜닝 결과', owner: '개발사', status: '예정', progress: 0, phase: '출력' },
    { id: '2.6', task: '2차 모델 학습', period: '8월', start: 8, end: 8, output: '2차 모델 학습 결과', owner: '개발사', status: '예정', progress: 0, phase: '출력' },
    { id: '2.7', task: '모델 학습 완료·내부 성능 점검', period: '9월', start: 9, end: 9, output: '내부 성능 점검 결과', owner: '개발사', status: '예정', progress: 0, phase: '검토' },
    { id: '2.8', task: '소프트웨어 단위·통합 시험', period: '10월', start: 10, end: 10, output: 'SUT · SIT 시험결과', owner: '개발사', status: '예정', progress: 0, phase: '검증' },
    { id: '2.9', task: '시스템 성능시험', period: '11월', start: 11, end: 11, output: 'SST · V&V 보고서 (#15)', owner: '개발사', status: '예정', progress: 0, phase: '검증' },
    { id: '2.10', task: '위험관리 결과 확정', period: '12월', start: 12, end: 12, output: 'Risk Management Report (#17)', owner: '개발사', status: '예정', progress: 0, phase: '출력' },
  ],
  2028: [
    { id: '2.11', task: '성능평가·통계분석 계획 수립', period: '1월', start: 1, end: 1, output: '성능평가·통계분석 계획서 (#22)', owner: '공동', status: '예정', progress: 0, phase: '검증' },
    { id: '2.12', task: '모델 검증 결과 확정', period: '2월', start: 2, end: 2, output: '모델 검증 최종 결과', owner: '공동', status: '예정', progress: 0, phase: '유효성' },
    { id: '3.1', task: '허가·품질관리 행정자료 준비', period: '3월', start: 3, end: 3, output: '제조업 허가·GMP 자료 (#1·2·3)', owner: '개발사', status: '예정', progress: 0, phase: '이관' },
    { id: '3.2', task: '제품 개요·품목 등급 검토', period: '4월', start: 4, end: 4, output: '제품 개요서·등급 검토자료 (#4·5)', owner: '개발사', status: '예정', progress: 0, phase: '이관' },
    { id: '3.3', task: '사용목적·대상·환경 정의', period: '5월', start: 5, end: 5, output: '사용목적·사용환경 자료 (#6)', owner: '개발사', status: '예정', progress: 0, phase: '이관' },
    { id: '3.4', task: '임상 안전성·유효성 평가', period: '6월', start: 6, end: 6, output: 'Clinical Evaluation Report (#24)', owner: '개발사', status: '예정', progress: 0, phase: '유효성' },
    { id: '3.5', task: '사용적합성·보안 검토', period: '7월', start: 7, end: 7, output: '사용적합성·사이버보안 자료 (#25)', owner: '개발사', status: '예정', progress: 0, phase: '이관' },
    { id: '3.6', task: '배포·유지보수·문제해결 절차 정의', period: '8월', start: 8, end: 8, output: '운영·유지보수 절차서 (#16)', owner: '개발사', status: '예정', progress: 0, phase: '출력' },
    { id: '3.7', task: '설계개발 종합 완료', period: '9월', start: 9, end: 9, output: '설계개발 완료 보고서 (DDR)', owner: '개발사', status: '예정', progress: 0, phase: '유효성' },
    { id: '3.8', task: '인허가 기술문서 구성·신청', period: '9월', start: 9, end: 9, output: '제품표준서·기술문서 (PS/TD)', owner: '개발사', status: '예정', progress: 0, phase: '이관' },
    { id: '3.9', task: '식약처 심사 및 보완 대응', period: '10–12월', start: 10, end: 12, output: '심사 보완자료·답변서', owner: '개발사', status: '예정', progress: 0, phase: '이관' },
    { id: '3.10', task: '계약기간 만료 검토', period: '12월', start: 12, end: 12, output: '계약 연장 여부 서면합의', owner: '공동', status: '예정', progress: 0, phase: '마일스톤' },
  ],
  2029: [
    { id: '4.1', task: '식약처 심사 대응 지속', period: '1–3월', start: 1, end: 3, output: '월별 심사 대응 기록', owner: '개발사', status: '예정', progress: 0, phase: '이관' },
    { id: '4.2', task: '최종 보완자료 제출', period: '4월', start: 4, end: 4, output: '최종 보완자료', owner: '개발사', status: '예정', progress: 0, phase: '이관' },
    { id: '4.3', task: '인허가 승인', period: '5월 예상', start: 5, end: 5, output: '디지털의료기기 인증서', owner: '개발사', status: '예정', progress: 0, phase: '마일스톤' },
    { id: '4.4', task: '사용자 매뉴얼·표시기재 확정', period: '6월 1–2주', start: 6, end: 6, output: '사용자 매뉴얼·주의사항 (#26)', owner: '공동', status: '예정', progress: 0, phase: '이관' },
    { id: '4.5', task: '설계 완료 및 이관 승인', period: '6월 1–2주', start: 6, end: 6, output: '설계완료 보고서 (DCR)', owner: '개발사', status: '예정', progress: 0, phase: '이관' },
    { id: '4.6', task: '운영·재학습 교육자료 완성', period: '6월 1–2주', start: 6, end: 6, output: '사용설명서·교육자료 (IFU/TM)', owner: '개발사', status: '예정', progress: 0, phase: '출력' },
    { id: '4.7', task: '버전·형상관리 체계 이관', period: '6월 3–4주', start: 6, end: 6, output: '소프트웨어 버전관리 대장 (RLN)', owner: '개발사', status: '예정', progress: 0, phase: '변경' },
    { id: '4.8', task: '협회 기술이전 교육', period: '6월', start: 6, end: 6, output: '기술이전 교육 결과', owner: '공동', status: '예정', progress: 0, phase: '이관' },
  ],
};

const outputDetails: Record<string, string> = {
  '1.1': '과업 목적, 개발 범위, 역할, 검수 기준 및 일정이 포함된 착수 승인 문서',
  '1.2': '적용 법규 목록, 사용자·시스템 요구사항 및 요구사항 추적 기준',
  '1.3': 'IRB 승인서, DRB 데이터 이용·반출 승인서, 심의 조건 및 보완요청 기록',
  '1.4': '프리킥오프에서 최대 20,000건, 구성군, 제공 가능 시점 및 방식을 확정한 기록',
  '1.5': '필수 임상변수와 정상·의심·확진 등 정답라벨 정의 및 판정 규칙',
  '1.6': '협회 보유·판정 가능·AI 활용 품질·비식별 완료 자료의 선정 및 재식별 위험·저품질·불명확·중복 자료의 제외 기준',
  '1.7': '데이터 편향·누락·유출 위험목록, 통제조치, 책임자 및 점검주기',
  '1.8': '비식별·영상 품질·중복 제거·라벨 검수 후 확정한 최종 목록, 제외 사유 및 QC 통계',
  '1.9': '설치 패키지, 사용자 계정·권한, 기능시험 기록 및 배포 안내',
  '1.10': 'DICOM 개인정보 제거 항목, 처리 절차, 샘플 검증 및 처리 로그',
  '1.11': '설치확인서, 입·출력 연계 시험 기록, 교육 참석자 및 결과',
  '1.12': '레이블 생성→검수→잠금→반출 흐름, 담당 역할 및 승인 기준',
  '1.13': '판독 가이드, 레이블 데이터, 검수 이력 및 오류·수정 로그',
  '1.14': '불일치 사례 목록, 전문의 재판독 결과 및 합의·수정 이력',
  '1.15': '최종 Ground Truth 정의, 판독자 합의 규칙 및 라벨 잠금 승인',
  '2.1': '비식별 CXR·임상정보·GT 라벨 묶음, 데이터 명세 및 인수인계서',
  '2.2': '모델 구조, 입력·출력, 전처리, 학습·추론 흐름 및 인터페이스 설계',
  '2.3': '사용 라이브러리·버전·라이선스·취약점 목록과 환경 재현 정보',
  '2.4': '모델 파일, 학습 설정, 학습곡선 및 1차 성능지표',
  '2.5': 'Fold별 성능, 오차분석, 하이퍼파라미터 변경 및 선정 근거',
  '2.6': '개선 모델 파일, 학습 재현정보 및 1·2차 성능 비교',
  '2.7': '민감도·특이도·AUC 등 내부 성능, 오류사례 및 출시 후보 결정',
  '2.8': '단위·통합 시험 항목, 입력·출력 예상값, 실행 결과 및 결함 조치',
  '2.9': '시스템 요구사항별 검증 결과, 성능·안정성 및 추적성 근거',
  '2.10': '위험별 통제 적용·잔여위험 평가, 검증 근거 및 승인 기록',
  '2.11': '평가 대상, 평가지표, 표본수, 통계방법 및 합격 기준',
  '2.12': '외부·독립 검증 성능표, 신뢰구간, 오류분석 및 최종 결론',
  '3.1': '제조업 허가증, 품질매뉴얼 및 GMP 적합성 제출·증빙자료',
  '3.2': '제품명·모델·버전·구성·작동원리와 품목분류·등급 판단 근거',
  '3.3': '의도된 용도, 대상 환자·사용자, 사용 장소 및 금기·제한사항',
  '3.4': '문헌·임상데이터 기반 안전성·유효성 평가와 이익·위험 결론',
  '3.5': '사용성 평가 계획·결과, 위협모델, 보안위험 및 통제 검증',
  '3.6': '배포·업데이트·장애·민원·CAPA·재학습 처리 절차와 책임',
  '3.7': '설계 산출물 완결성, 미해결 이슈 및 검증·승인 상태 종합 보고',
  '3.8': '제품표준서, 기술문서 목차·본문·첨부자료, 신청서 및 제출본',
  '3.9': '보완요청 목록, 항목별 답변, 수정 기술문서 및 제출·협의 기록',
  '3.10': '종료·연장 판단, 잔여업무·비용·기간 및 양측 서명 합의서',
  '4.1': '월별 질의·답변, 제출자료 버전 및 협의·후속조치 추적대장',
  '4.2': '미해결 보완사항 최종 답변, 수정본 및 제출 확인증',
  '4.3': '허가 품목명·모델·사용목적·조건이 명시된 최종 인증서',
  '4.4': '설치·사용·주의·금기·오류대응 및 표시기재 최종본',
  '4.5': '설계 산출물 검토·승인, 잔여 이슈 종료 및 이관 승인 서명',
  '4.6': '운영자용 사용설명서, 설치·점검·재학습 절차 및 교육 교안',
  '4.7': '소프트웨어 버전, 변경내역, 빌드·배포 정보 및 형상항목 인계 목록',
  '4.8': '교육자료, 참석자·실습 기록, 평가 결과 및 기술이전 완료 확인서',
};

const statusFilters: FilterValue[] = ['전체', '완료', '진행 중', '예정'];

function statusClass(status: Status) {
  return status.replace(' ', '');
}

function StatusBadge({ status }: { status: Status }) {
  return <span className={`status-badge status-${statusClass(status)}`}>{status}</span>;
}

export default function Home() {
  const [selectedYear, setSelectedYear] = useState(2026);
  const [statusFilter, setStatusFilter] = useState<FilterValue>('전체');
  const tasks = wbs[selectedYear];
  const info = yearInfo[selectedYear];

  const visibleTasks = useMemo(
    () => tasks.filter((task) => statusFilter === '전체' || task.status === statusFilter),
    [tasks, statusFilter],
  );

  const completed = tasks.filter((task) => task.status === '완료').length;
  const inProgress = tasks.filter((task) => task.status === '진행 중').length;

  function selectYear(year: number) {
    setSelectedYear(year);
    setStatusFilter('전체');
  }

  return (
    <main>
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand-mark">TB</div>
          <div>
            <p className="brand-title">결핵 진단 AI 공동연구</p>
            <p className="brand-sub">대한결핵협회 × ㈜마이허브</p>
          </div>
          <span className="asof">2026.09.02 기준</span>
        </div>
      </header>

      <div className="page-shell">
        <section className="intro">
          <div>
            <p className="eyebrow">PROJECT WORK BREAKDOWN STRUCTURE</p>
            <h1>업무·일정·산출물을 한눈에</h1>
            <p className="intro-copy">월간 일정표 구조에 상태와 진척률을 더한 프로젝트 실행 현황입니다.</p>
          </div>
          <div className="intro-actions">
            <button className="print-button" type="button" onClick={() => window.print()}>
              <Printer data-icon="inline-start" /> 인쇄
            </button>
            <div className="year-switch" aria-label="연도 선택">
              {Object.keys(wbs).map((yearString) => {
                const year = Number(yearString);
                return (
                  <button
                    key={year}
                    type="button"
                    aria-pressed={selectedYear === year}
                    className={`year-button ${selectedYear === year ? 'is-active' : ''}`}
                    onClick={() => selectYear(year)}
                  >
                    {year}
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        <section className="summary-grid" aria-label={`${selectedYear}년 프로젝트 요약`}>
          <article className="summary-card accent-card">
            <div className="summary-icon"><Flag /></div>
            <div><span>{selectedYear} 전체 진척률</span><strong>{info.progress}%</strong></div>
            <div className="summary-progress"><i style={{ width: `${info.progress}%` }} /></div>
          </article>
          <article className="summary-card">
            <div className="summary-icon is-green"><Check /></div>
            <div><span>완료 업무</span><strong>{completed}</strong><small>/ {tasks.length}</small></div>
          </article>
          <article className="summary-card">
            <div className="summary-icon is-orange"><CalendarDays /></div>
            <div><span>진행 중</span><strong>{inProgress}</strong><small>건</small></div>
          </article>
          <article className="summary-card">
            <div className="summary-icon is-blue"><FileCheck2 /></div>
            <div><span>핵심 산출물</span><strong>{tasks.length}</strong><small>종</small></div>
          </article>
        </section>

        {selectedYear === 2026 ? (
          <>
            <section className="now-panel">
              <div className="now-label"><span className="pulse-dot" />NOW · 8월 25일 착수</div>
              <div className="now-copy">
                <strong>과제 착수 및 개발 범위 정의 진행 중</strong>
                <span>9월 4일 프리킥오프에서 데이터 범위·규모와 제공 조건을 확인합니다.</span>
              </div>
              <ChevronRight className="now-arrow" />
            </section>

            <section className="dataset-panel" aria-labelledby="dataset-scope-title">
              <div className="dataset-head">
                <div>
                  <span>9월 4일 프리킥오프 확인용 초안</span>
                  <h2 id="dataset-scope-title">데이터셋 구성 및 선정·제외 기준</h2>
                </div>
                <div className="dataset-total"><strong>20,000건 이내</strong><small>비식별 흉부 X-ray 영상</small></div>
              </div>
              <div className="dataset-grid">
                <article>
                  <h3>구성군</h3>
                  <div className="dataset-chips"><span>활동성 결핵</span><span>비활동성 결핵</span><span>정상군</span><span>기타 폐질환군 · 필요 시</span></div>
                  <p>기존 판독 또는 진단 정보를 기준으로 구성하고 가능한 범위에서 군별 균형을 고려합니다.</p>
                </article>
                <article>
                  <h3>선정기준</h3>
                  <ul>
                    <li>대한결핵협회가 보유한 흉부 X-ray</li>
                    <li>활동성·비활동성 결핵 또는 정상 판정 가능</li>
                    <li>AI 학습·검증에 활용 가능한 영상 품질</li>
                    <li>연구자 제공 전 비식별 조치 완료</li>
                  </ul>
                </article>
                <article>
                  <h3>제외기준</h3>
                  <ul>
                    <li>비식별 후에도 개인 식별 가능성이 있는 자료</li>
                    <li>판독·학습에 부적합한 저품질 영상</li>
                    <li>진단 또는 판독 결과가 불명확한 자료</li>
                    <li>중복자료 또는 연구목적에 부적합한 자료</li>
                  </ul>
                </article>
              </div>
              <div className="dataset-rule"><strong>분할·확정 원칙</strong><span>학습용·검증용·시험용으로 분할하며 동일 대상자·동일 영상의 데이터셋 간 중복을 방지합니다. 최종 건수는 비식별, 품질검토, 중복 제거, 라벨 검수 및 연구목적 적합성 검토 후 확정합니다.</span></div>
            </section>
          </>
        ) : (
          <section className="year-note">
            <span>{selectedYear} 실행 흐름</span>
            <strong>{info.note}</strong>
          </section>
        )}

        <section className="wbs-section">
          <div className="section-head">
            <div>
              <p className="section-kicker">{selectedYear} WBS</p>
              <h2>{info.title}</h2>
            </div>
            <div className="section-tools">
              <div className="status-filters" aria-label="상태 필터">
                <Filter />
                {statusFilters.map((filter) => (
                  <button
                    key={filter}
                    type="button"
                    aria-pressed={statusFilter === filter}
                    className={`filter-button ${statusFilter === filter ? 'is-active' : ''}`}
                    onClick={() => setStatusFilter(filter)}
                  >
                    {filter}
                  </button>
                ))}
              </div>
              <div className="legend" aria-label="상태 범례">
                <span><i className="legend-done" />완료</span>
                <span><i className="legend-progress" />진행 중</span>
                <span><i className="legend-plan" />예정</span>
              </div>
            </div>
          </div>

          <div className="wbs-table-wrap">
            <div className="wbs-table" role="table" aria-label={`${selectedYear}년 업무 일정 및 산출물`}>
              <div className="wbs-row wbs-head" role="row">
                <div role="columnheader" className="task-head">TASK</div>
                <div role="columnheader" className={`schedule-head ${selectedYear === 2026 ? 'is-current' : ''}`}>
                  <span>추진 일정</span>
                  <div className="month-grid">
                    {months.map((month) => <span key={month}>{month}</span>)}
                  </div>
                </div>
                <div role="columnheader">산출물 / 확인 내용</div>
                <div role="columnheader">상태 / 진척률</div>
              </div>

              {visibleTasks.length > 0 ? visibleTasks.map((item) => (
                <div className="wbs-row" role="row" key={item.id}>
                  <div className="task-cell" role="cell">
                    <span className="task-id">{item.id}</span>
                    <div>
                      <strong>{item.task}</strong>
                      <small><span className="phase-chip">{item.phase}</span>{item.owner} · {item.period}</small>
                    </div>
                  </div>
                  <div className={`timeline-cell ${selectedYear === 2026 ? 'is-current' : ''}`} role="cell">
                    <div className="month-grid month-cells">
                      {months.map((month) => <span key={month} />)}
                    </div>
                    <div
                      className={`timeline-bar bar-${statusClass(item.status)}`}
                      style={{
                        left: `${((item.start - 1) / 12) * 100}%`,
                        width: `${((item.end - item.start + 1) / 12) * 100}%`,
                      }}
                      title={`${item.task}: ${item.period}`}
                    >
                      {item.period}
                    </div>
                  </div>
                  <div className="output-cell" role="cell">
                    <ClipboardList />
                    <div>
                      <strong>{item.output}</strong>
                      <small><b>확인 내용</b>{outputDetails[item.id]}</small>
                    </div>
                  </div>
                  <div className="progress-cell" role="cell">
                    <div><StatusBadge status={item.status} /><b>{item.progress}%</b></div>
                    <span className="row-progress"><i style={{ width: `${item.progress}%` }} /></span>
                  </div>
                </div>
              )) : (
                <div className="empty-row">선택한 상태에 해당하는 업무가 없습니다.</div>
              )}
            </div>
          </div>

          <footer className="table-footer">
            <span>※ 기준선 변경: 2026.08.25 착수 기준으로 후속 일정을 순연했으며, 일부 업무는 2027–2028년으로 이월했습니다. 세부 일정은 실무 협의에 따른 추정안입니다.</span>
            <strong>{visibleTasks.length}개 업무 표시</strong>
          </footer>
        </section>
      </div>
    </main>
  );
}

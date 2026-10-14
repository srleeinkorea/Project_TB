import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: new URL('https://tb-ai-wbs-2026.maihub-inc-3182.chatgpt.site'),
  title: '결핵 진단 AI · 프로젝트 WBS',
  description: '결핵 진단 AI 공동연구의 업무, 일정, 산출물 및 진척 현황',
  openGraph: {
    title: '결핵 진단 AI 프로젝트 WBS',
    description: '업무 · 일정 · 산출물 · 진척 현황',
    images: [{ url: '/og.png', width: 1200, height: 630, alt: '결핵 진단 AI 프로젝트 WBS' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: '결핵 진단 AI 프로젝트 WBS',
    description: '업무 · 일정 · 산출물 · 진척 현황',
    images: ['/og.png'],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}

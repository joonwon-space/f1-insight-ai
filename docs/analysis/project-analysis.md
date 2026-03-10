# F1 Insight AI - Project Analysis

> 이 파일은 각 태스크 완료 후 자동으로 업데이트됩니다.

---

## 1. 현재 진행 상황

| Phase | 완료 | 전체 | 진행률 |
|-------|------|------|--------|
| Phase 0: Project Init | 2 | 3 | 67% |
| Phase 1: 백엔드 기반 구축 | 4 | 4 | 100% |
| Phase 2: 데이터 수집 파이프라인 | 4 | 4 | 100% |
| Phase 3: LLM 요약/번역 파이프라인 | 4 | 4 | 100% |
| Phase 4: REST API 엔드포인트 | 4 | 4 | 100% |
| Phase 5: React + shadcn/ui 프론트엔드 | 2 | 6 | 33% |
| Phase 6: DevOps | 0 | 4 | 0% |
| Phase 7: YouTube (장기) | 0 | 5 | 0% |
| **전체** | **19** | **34** | **56%** |

> ※ 백엔드 Phase 1~3은 이전 세션에서 구현됨 (Ollama 기반, 새 tasks.md 기준으로 재계산)

**마지막 완료 태스크**: Task 5.2 — 레이아웃 및 공통 컴포넌트
**다음 태스크**: Task 5.3 — 뉴스 목록 페이지

---

## 2. 아키텍처 현황

### 구현된 컴포넌트
- [x] `.env.example` — VITE_API_URL, OPENAI_API_KEY, ANTHROPIC_API_KEY, UNSPLASH_ACCESS_KEY, CLOUDFLARE_TUNNEL_TOKEN
- [x] `.gitignore` — Vite `dist/`, `.vite/` 추가, `.next/` 제거
- [x] `backend/pyproject.toml` — feedparser, openai, anthropic 추가
- [x] `CLAUDE.md` — React + Vite + shadcn/ui 기준으로 업데이트
- [x] Frontend 골격 — Vite + React 19 + TypeScript + Tailwind CSS v4 기본 구조
- [x] Backend (FastAPI 앱, Core 모듈) — 이전 세션
- [x] Backend scraper (HTTP 클라이언트, HTML 파서, 중복 감지) — 이전 세션
- [x] Backend scheduler (APScheduler, 동적 모드 전환) — 이전 세션
- [x] Backend LLM (OpenAI 클라이언트, 요약, 번역, 태깅) — 이전 세션
- [x] Backend services (MongoDB 스키마, ES 매핑, 동기화) — 이전 세션

### 미구현 컴포넌트 (새 tasks.md 기준)
- [ ] Docker Compose — MongoDB, ES, backend, frontend (0.2)
- [ ] Cloudflare Tunnel 설정 (0.3)
- [ ] RSS 피드 수집 — feedparser 기반 (2.1)
- [ ] REST API 엔드포인트 (Phase 4)
- [ ] React 프론트엔드 상세 구현 (Phase 5)

---

## 3. 기술 스택 상세

### Backend
| 패키지 | 버전 | 상태 |
|--------|------|------|
| fastapi | >=0.115 | 사용중 |
| motor | >=3.6 | 사용중 |
| elasticsearch[async] | >=8.17 | 사용중 |
| httpx | >=0.28 | 사용중 |
| beautifulsoup4 | >=4.12 | 사용중 |
| apscheduler | >=3.10 | 사용중 |
| fastf1 | >=3.4 | 사용중 |
| feedparser | >=6.0 | **새로 추가** |
| openai | >=1.0 | **새로 추가** |
| anthropic | >=0.40 | **새로 추가** |
| pdfplumber | >=0.11 | 사용중 (transcript) |

### Frontend (새 스택)
| 패키지 | 버전 | 상태 |
|--------|------|------|
| react | ^19.0.0 | 추가됨 |
| react-dom | ^19.0.0 | 추가됨 |
| react-router-dom | ^7.0.0 | 추가됨 |
| vite | ^6.0.0 | 추가됨 |
| tailwindcss | ^4.0.0 | 추가됨 |
| @radix-ui/* | ^1-2.x | 추가됨 |
| shadcn/ui (via radix) | - | 추가됨 |
| lucide-react | ^0.460.0 | 추가됨 |

---

## 4. 파일 구조

### Frontend (새 구조)
```
frontend/
├── index.html              # Vite SPA 진입점
├── vite.config.ts          # Vite + Tailwind CSS v4 + @ alias
├── tsconfig.json           # 프로젝트 references
├── tsconfig.app.json       # 앱 소스 TypeScript 설정
├── tsconfig.node.json      # Vite 설정용 TypeScript
├── package.json            # React 19 + Vite + shadcn deps
├── eslint.config.js        # ESLint flat config
├── nginx.conf              # 프로덕션 SPA nginx 설정
├── Dockerfile              # Vite 빌드 + nginx 서빙
├── public/
│   └── vite.svg            # 기본 favicon
└── src/
    ├── main.tsx            # React 19 진입점
    ├── App.tsx             # Root + React Router
    ├── index.css           # Tailwind CSS v4 + F1 디자인 토큰
    ├── components/
    │   └── layout/
    │       ├── Header.tsx  # 네비게이션 (React Router Link)
    │       └── Sidebar.tsx # 필터 사이드바 (placeholder)
    └── lib/
        ├── api.ts          # API 클라이언트 (VITE_API_URL)
        └── utils.ts        # shadcn/ui cn() 유틸리티
```

### Backend (기존 구조 유지)
```
backend/app/
├── main.py, api/, core/
├── scraper/ — HTTP 클라이언트, HTML 파서, transcript 파서
├── scheduler/ — APScheduler 동적 스케줄러
├── llm/ — OpenAI/Ollama 클라이언트, 요약/번역/태깅
├── models/ — Pydantic v2 스키마
└── services/ — MongoDB repository, ES 인덱서/검색, 동기화
```

---

## 5. 이슈 및 개선 사항

- **ollama_client.py 잔존**: 이전 세션에서 Ollama 클라이언트가 구현됨. 새 스택은 외부 API만 사용하므로 추후 Task 3.1에서 정리 필요
- **node_modules 구버전**: frontend/node_modules는 Next.js 패키지를 담고 있음. `npm install` 필요 (Docker 빌드 시 자동 처리)
- **RSS 수집 미구현**: feedparser가 pyproject.toml에 추가됐으나 실제 RSS 파서 모듈은 Task 2.1에서 구현 예정

---

## 6. 태스크 완료 로그

| 태스크 | 완료일 | 요약 |
|--------|--------|------|
| Phase 0 (0.1) | 2026-03-10 | React+Vite 전환: .env.example, .gitignore, pyproject.toml, frontend 구조 재정립 |
| Phase 0 (0.2) | 2026-03-10 | Docker Compose: frontend 포트 3000:80, backend 멀티스테이지 빌드, build args VITE_API_URL |
| Phase 1 (1.1~1.4) | 2026-03-10 | FastAPI 앱, MongoDB 스키마/Repository, ES 매핑/검색, 동기화 — 이전 세션에서 구현 |
| Phase 2 (2.2~2.4) | 2026-03-10 | HTML 스크래퍼, FastF1 클라이언트, APScheduler — 이전 세션에서 구현 |
| Phase 3 (3.1~3.4) | 2026-03-10 | OpenAI/Anthropic LLM 클라이언트, 요약/번역/태깅 파이프라인 — 이전 세션에서 구현 |
| Task 2.1 | 2026-03-10 | feedparser RSS 수집: sources.py, parser.py, service.py, 스케줄러 통합 |
| Task 4.1-4.4 | 2026-03-10 | REST API: /api/news, /api/search, /api/schedule, /api/teams, /api/drivers, /api/images/search |
| Task 5.1-5.2 | 2026-03-10 | shadcn/ui 컴포넌트 (Button, Badge, Card, Skeleton, Sheet, Input), RootLayout, Header, Sidebar, 페이지 스캐폴딩 |

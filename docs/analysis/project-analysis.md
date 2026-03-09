# F1 Insight AI - Project Analysis

> 이 파일은 각 태스크 완료 후 자동으로 업데이트됩니다.
> 프로젝트 현황을 파악하고, 추후 tasks.md에 새 태스크를 추가할 때 참고합니다.

---

## 1. 현재 진행 상황

| Phase | 완료 | 전체 | 진행률 |
|-------|------|------|--------|
| Phase 0: Project Init | 4 | 4 | 100% |
| Phase 1: Data Collection | 0 | 4 | 0% |
| Phase 2: Data Storage | 0 | 3 | 0% |
| Phase 3: LLM Pipeline | 0 | 4 | 0% |
| Phase 4: API & Frontend | 0 | 4 | 0% |
| Phase 5: DevOps | 0 | 4 | 0% |
| Phase 6: YouTube (확장) | 0 | 4 | 0% |
| **전체** | **4** | **27** | **15%** |

**마지막 완료 태스크**: Task 0.4 — Next.js 프론트엔드 보일러플레이트
**다음 태스크**: Task 1.1 — FastF1 세션 스케줄 통합
**Phase 0 완료!** Phase 1 (Data Collection) 진입.

---

## 2. 아키텍처 현황

### 구현된 컴포넌트
- [x] 프로젝트 디렉토리 구조 (backend/, frontend/, docs/)
- [x] FastAPI 앱 — lifespan 관리, CORS, 라우터 포함 (`backend/app/main.py`)
- [x] Pydantic Settings 설정 모듈 (`backend/app/core/config.py`)
- [x] MongoDB 연결 모듈 — Motor async driver (`backend/app/core/database.py`)
- [x] Elasticsearch 연결 모듈 — async client (`backend/app/core/elasticsearch.py`)
- [x] API 라우터 구조 + 의존성 상태 포함 health check (`backend/app/api/router.py`)
- [x] Next.js 15 레이아웃 — Header + Sidebar + Main 구조 (`frontend/src/app/layout.tsx`)
- [x] Header 컴포넌트 — F1 브랜딩, 네비게이션 (`frontend/src/components/layout/Header.tsx`)
- [x] Sidebar 컴포넌트 — 필터 플레이스홀더 (`frontend/src/components/layout/Sidebar.tsx`)
- [x] 랜딩 페이지 — 기능 소개 카드, 바이링궈 (`frontend/src/app/page.tsx`)
- [x] F1 테마 CSS — 다크 테마, F1 레드 (`frontend/src/app/globals.css`)
- [x] Docker Compose 프로덕션-레디 구성 (네트워크, 헬스체크, 메모리 제한, restart policy)
- [x] pyproject.toml 의존성 정의
- [x] API 클라이언트 유틸리티 (`frontend/src/lib/api.ts`)

### 미구현 컴포넌트
- [ ] 스크래퍼 모듈
- [ ] LLM 파이프라인
- [ ] 스케줄러
- [ ] REST API 엔드포인트 (news, search, schedule 등)
- [ ] MongoDB/Elasticsearch 스키마 및 인덱스
- [ ] 프론트엔드 데이터 연동 페이지 (뉴스 목록, 상세, 캘린더)
- [ ] CI/CD

---

## 3. 기술 스택 상세

### Backend
| 패키지 | 버전 | 상태 | 용도 |
|---------|------|------|------|
| FastAPI | >=0.115 | 사용중 | REST API, lifespan, CORS |
| Motor | >=3.6 | 사용중 | MongoDB async 연결/ping |
| elasticsearch[async] | >=8.17 | 사용중 | Elasticsearch 연결/ping |
| Pydantic | >=2.10 | 사용중 | 모델 (config via pydantic-settings) |
| pydantic-settings | >=2.7 | 사용중 | 환경 변수 설정 |
| uvicorn | >=0.34 | 사용중 | ASGI 서버 |
| httpx | >=0.28 | pyproject.toml에 정의, 미사용 | HTTP client |
| beautifulsoup4 | >=4.12 | pyproject.toml에 정의, 미사용 | 파싱 |
| APScheduler | >=3.10 | pyproject.toml에 정의, 미사용 | 스케줄링 |
| FastF1 | >=3.4 | pyproject.toml에 정의, 미사용 | F1 데이터 |

### Frontend
| 패키지 | 상태 | 용도 |
|---------|------|------|
| Next.js 15 (16.1.6) | 사용중 | App Router, SSR |
| React 19 | 사용중 | UI 라이브러리 |
| TypeScript | 사용중 | 타입 시스템 (strict) |
| Tailwind CSS v4 | 사용중 | 스타일링, F1 테마 |

### Infrastructure
| 서비스 | 이미지 | 상태 |
|---------|--------|------|
| MongoDB | mongo:7 | docker-compose 구성 완료 (헬스체크, 네트워크, 볼륨) |
| Elasticsearch | 8.17.0 | docker-compose 구성 완료 (mem_limit 1g, ulimits, 헬스체크) |
| Backend | python:3.12-slim | Dockerfile 있음 |
| Frontend | node:22-alpine | Dockerfile 있음 (multi-stage) |

---

## 4. 파일 구조

```
f1-insight-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 앱 (lifespan, CORS, 라우터)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── router.py        # API 라우터 + health check
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Pydantic Settings (환경 변수)
│   │   │   ├── database.py      # MongoDB Motor 연결 모듈
│   │   │   └── elasticsearch.py # Elasticsearch async 연결 모듈
│   │   ├── llm/__init__.py      # LLM 모듈 (비어있음)
│   │   ├── models/__init__.py   # 모델 (비어있음)
│   │   ├── scheduler/__init__.py # 스케줄러 (비어있음)
│   │   ├── scraper/__init__.py  # 스크래퍼 (비어있음)
│   │   └── services/__init__.py # 서비스 (비어있음)
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # 루트 레이아웃 (Header + Sidebar + Main)
│   │   │   ├── page.tsx         # 랜딩 페이지 (F1 Insight AI 소개)
│   │   │   ├── globals.css      # F1 테마 CSS (다크 모드, F1 레드)
│   │   │   └── favicon.ico
│   │   ├── components/
│   │   │   └── layout/
│   │   │       ├── Header.tsx   # 헤더 (브랜딩, 네비게이션)
│   │   │       └── Sidebar.tsx  # 사이드바 (필터 플레이스홀더)
│   │   └── lib/
│   │       └── api.ts           # API 클라이언트
│   ├── Dockerfile               # Multi-stage build
│   ├── package.json
│   └── tsconfig.json
├── docs/
│   ├── analysis/
│   │   └── project-analysis.md  # 이 파일
│   ├── plan/
│   │   └── tasks.md
│   └── project-overview.md
├── docker-compose.yml
├── .env.example
├── CLAUDE.md
└── README.md
```

---

## 5. 이슈 및 개선 사항

### 현재 이슈
- Docker가 호스트에 설치되지 않아 `docker compose config` 검증 미완료 (YAML 구조는 유효)
- Python 3.12+ 및 ruff가 호스트에 미설치 — 로컬 lint/test 불가 (Docker 내에서 실행 필요)

### 기술 부채
- CORS `allow_origins=["*"]` — 프로덕션 배포 시 특정 도메인으로 제한 필요.
- Sidebar 모바일 대응 미완성 — `lg` 이하에서 숨김 처리만. 햄버거 메뉴 토글 필요.
- 네비게이션 활성 상태 표시 없음 — `usePathname` 사용 시 `'use client'` 필요.

### 리스크
- FastF1 라이브러리가 2026 시즌 데이터를 지원하는지 확인 필요
- Elasticsearch 메모리 설정 (512MB) — Mac Mini 스펙에 따라 조정 필요
- 뉴스 사이트 스크래핑 정책 변경 가능성

---

## 6. 태스크 완료 로그

| 태스크 | 완료일 | 커밋 | 요약 |
|--------|--------|------|------|
| Task 0.1 | 2026-03-10 | 008f18e | 프로젝트 디렉토리 구조, pyproject.toml, docker-compose.yml 스켈레톤, Next.js 초기화 |
| Task 0.2 | 2026-03-10 | c677813 | Docker Compose 인프라: 커스텀 네트워크, 헬스체크 강화, ES 메모리 제한, restart policy |
| Task 0.3 | 2026-03-10 | 1b6bc68 | FastAPI 보일러플레이트: core 모듈(config, database, elasticsearch), 라우터 구조, lifespan 관리, health check |
| Task 0.4 | 2026-03-10 | (pending) | Next.js 보일러플레이트: Header/Sidebar 레이아웃 컴포넌트, 랜딩 페이지, F1 다크 테마 |

---

## 7. 추후 태스크 제안

> 여기에 tasks.md에 추가할 새 태스크 아이디어를 기록합니다.

- MongoDB 인증 추가 (프로덕션 배포 시 MONGO_INITDB_ROOT_USERNAME/PASSWORD 설정)
- Docker Compose 프로파일 분리 (dev / production) 검토
- CORS 설정 프로덕션 강화 (allow_origins를 특정 도메인으로 제한)
- 로깅 설정 모듈화 (구조화된 JSON 로깅, 로그 레벨 설정 환경 변수화)
- 모바일 반응형 네비게이션 (햄버거 메뉴, 사이드바 토글)
- 네비게이션 활성 상태 표시 (usePathname 기반)

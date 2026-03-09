# F1 Insight AI - Project Analysis

> 이 파일은 각 태스크 완료 후 자동으로 업데이트됩니다.
> 프로젝트 현황을 파악하고, 추후 tasks.md에 새 태스크를 추가할 때 참고합니다.

---

## 1. 현재 진행 상황

| Phase | 완료 | 전체 | 진행률 |
|-------|------|------|--------|
| Phase 0: Project Init | 4 | 4 | 100% |
| Phase 1: Data Collection | 1 | 4 | 25% |
| Phase 2: Data Storage | 0 | 3 | 0% |
| Phase 3: LLM Pipeline | 0 | 4 | 0% |
| Phase 4: API & Frontend | 0 | 4 | 0% |
| Phase 5: DevOps | 0 | 4 | 0% |
| Phase 6: YouTube (확장) | 0 | 4 | 0% |
| **전체** | **5** | **27** | **19%** |

**마지막 완료 태스크**: Task 1.1 — FastF1 세션 스케줄 통합
**다음 태스크**: Task 1.2 — F1 뉴스 스크래퍼 구현

---

## 2. 아키텍처 현황

### 구현된 컴포넌트
- [x] 프로젝트 디렉토리 구조 (backend/, frontend/, docs/)
- [x] FastAPI 앱 — lifespan 관리, CORS, 라우터 포함 (`backend/app/main.py`)
- [x] Pydantic Settings 설정 모듈 (`backend/app/core/config.py`)
- [x] MongoDB 연결 모듈 — Motor async driver (`backend/app/core/database.py`)
- [x] Elasticsearch 연결 모듈 — async client (`backend/app/core/elasticsearch.py`)
- [x] API 라우터 구조 + 의존성 상태 포함 health check (`backend/app/api/router.py`)
- [x] F1 스케줄 Pydantic 모델 (`backend/app/models/schedule.py`)
- [x] FastF1 클라이언트 래퍼 (`backend/app/services/fastf1_client.py`)
- [x] 스케줄 서비스 — FastF1 + 폴백 (`backend/app/services/schedule.py`)
- [x] 2026 시즌 하드코딩 데이터 (`backend/app/services/schedule_data_2026.py`)
- [x] Next.js 15 레이아웃 — Header + Sidebar + Main 구조
- [x] Header/Sidebar 레이아웃 컴포넌트
- [x] 랜딩 페이지 — F1 테마 다크 모드
- [x] Docker Compose 프로덕션-레디 구성
- [x] API 클라이언트 유틸리티 (`frontend/src/lib/api.ts`)

### 미구현 컴포넌트
- [ ] 뉴스 스크래퍼 모듈
- [ ] FIA 프레스 컨퍼런스 파서
- [ ] 동적 스케줄러
- [ ] LLM 파이프라인
- [ ] REST API 엔드포인트 (news, search, schedule 등)
- [ ] MongoDB/Elasticsearch 스키마 및 인덱스
- [ ] 프론트엔드 데이터 연동 페이지
- [ ] CI/CD

---

## 3. 기술 스택 상세

### Backend
| 패키지 | 버전 | 상태 | 용도 |
|---------|------|------|------|
| FastAPI | >=0.115 | 사용중 | REST API, lifespan, CORS |
| Motor | >=3.6 | 사용중 | MongoDB async 연결/ping |
| elasticsearch[async] | >=8.17 | 사용중 | Elasticsearch 연결/ping |
| Pydantic | >=2.10 | 사용중 | 모델, 스케줄 데이터 구조 |
| pydantic-settings | >=2.7 | 사용중 | 환경 변수 설정 |
| uvicorn | >=0.34 | 사용중 | ASGI 서버 |
| FastF1 | >=3.4 | 사용중 | F1 세션 스케줄 조회 (폴백 포함) |
| httpx | >=0.28 | pyproject.toml에 정의, 미사용 | HTTP client |
| beautifulsoup4 | >=4.12 | pyproject.toml에 정의, 미사용 | 파싱 |
| APScheduler | >=3.10 | pyproject.toml에 정의, 미사용 | 스케줄링 |

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
| MongoDB | mongo:7 | docker-compose 구성 완료 |
| Elasticsearch | 8.17.0 | docker-compose 구성 완료 |
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
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schedule.py      # 스케줄 Pydantic 모델 (Session, RaceEvent 등)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── schedule.py      # 스케줄 서비스 (FastF1 + 폴백)
│   │   │   ├── fastf1_client.py # FastF1 래퍼 (캐시, 비동기)
│   │   │   └── schedule_data_2026.py # 2026 시즌 하드코딩 데이터
│   │   ├── llm/__init__.py
│   │   ├── scheduler/__init__.py
│   │   └── scraper/__init__.py
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # 루트 레이아웃 (Header + Sidebar + Main)
│   │   │   ├── page.tsx         # 랜딩 페이지
│   │   │   ├── globals.css      # F1 테마 CSS
│   │   │   └── favicon.ico
│   │   ├── components/layout/
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   └── lib/api.ts
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── docs/
│   ├── analysis/project-analysis.md
│   ├── plan/tasks.md
│   └── project-overview.md
├── docker-compose.yml
├── .env.example
├── CLAUDE.md
└── README.md
```

---

## 5. 이슈 및 개선 사항

### 현재 이슈
- Docker가 호스트에 설치되지 않아 `docker compose config` 검증 미완료
- Python 3.12+ 및 ruff가 호스트에 미설치 — 로컬 lint/test 불가

### 기술 부채
- CORS `allow_origins=["*"]` — 프로덕션 배포 시 제한 필요
- Sidebar 모바일 대응 미완성 — 햄버거 메뉴 토글 필요
- 네비게이션 활성 상태 표시 없음
- `_SESSION_DURATIONS` 상수가 `fastf1_client.py`와 `schedule.py`에 중복 정의됨

### 리스크
- FastF1이 2026 시즌 데이터를 지원하지 않을 가능성 높음 → 폴백 데이터로 대응 완료
- 2026 시즌 일정은 추정치 — 실제 FIA 발표 후 업데이트 필요
- Elasticsearch 메모리 설정 (512MB) — Mac Mini 스펙에 따라 조정 필요

---

## 6. 태스크 완료 로그

| 태스크 | 완료일 | 커밋 | 요약 |
|--------|--------|------|------|
| Task 0.1 | 2026-03-10 | 008f18e | 프로젝트 디렉토리 구조, pyproject.toml, docker-compose.yml 스켈레톤, Next.js 초기화 |
| Task 0.2 | 2026-03-10 | c677813 | Docker Compose 인프라: 커스텀 네트워크, 헬스체크, ES 메모리 제한 |
| Task 0.3 | 2026-03-10 | 1b6bc68 | FastAPI 보일러플레이트: core 모듈, 라우터 구조, lifespan, health check |
| Task 0.4 | 2026-03-10 | cc7ca3a | Next.js 보일러플레이트: Header/Sidebar 레이아웃, 랜딩 페이지, F1 다크 테마 |
| Task 1.1 | 2026-03-10 | (pending) | FastF1 스케줄 통합: 세션/이벤트 모델, FastF1 래퍼, 2026 폴백 데이터, 현재/다음 세션 감지 |

---

## 7. 추후 태스크 제안

- MongoDB 인증 추가 (프로덕션 배포 시)
- Docker Compose 프로파일 분리 (dev / production)
- CORS 설정 프로덕션 강화
- 로깅 모듈화 (JSON 로깅, 로그 레벨 환경 변수화)
- 모바일 반응형 네비게이션
- 스케줄 데이터 자동 업데이트 메커니즘 (FIA 공식 발표 시)
- `_SESSION_DURATIONS` 중복 제거 → 공통 상수로 추출

# F1 Insight AI - Project Analysis

> 이 파일은 각 태스크 완료 후 자동으로 업데이트됩니다.
> 프로젝트 현황을 파악하고, 추후 tasks.md에 새 태스크를 추가할 때 참고합니다.

---

## 1. 현재 진행 상황

| Phase | 완료 | 전체 | 진행률 |
|-------|------|------|--------|
| Phase 0: Project Init | 4 | 4 | 100% |
| Phase 1: Data Collection | 2 | 4 | 50% |
| Phase 2: Data Storage | 0 | 3 | 0% |
| Phase 3: LLM Pipeline | 0 | 4 | 0% |
| Phase 4: API & Frontend | 0 | 4 | 0% |
| Phase 5: DevOps | 0 | 4 | 0% |
| Phase 6: YouTube (확장) | 0 | 4 | 0% |
| **전체** | **6** | **27** | **22%** |

**마지막 완료 태스크**: Task 1.2 — F1 뉴스 스크래퍼 구현
**다음 태스크**: Task 1.3 — FIA 프레스 컨퍼런스 트랜스크립트 파서

---

## 2. 아키텍처 현황

### 구현된 컴포넌트
- [x] 프로젝트 디렉토리 구조 (backend/, frontend/, docs/)
- [x] FastAPI 앱 — lifespan, CORS, 라우터 (`backend/app/main.py`)
- [x] Pydantic Settings (`backend/app/core/config.py`)
- [x] MongoDB 연결 모듈 (`backend/app/core/database.py`)
- [x] Elasticsearch 연결 모듈 (`backend/app/core/elasticsearch.py`)
- [x] API 라우터 + health check (`backend/app/api/router.py`)
- [x] F1 스케줄 모델 + 서비스 (`models/schedule.py`, `services/schedule.py`)
- [x] FastF1 클라이언트 + 2026 폴백 데이터
- [x] 뉴스 기사 모델 (`models/article.py`) — RawArticle, ArticleDocument
- [x] 비동기 HTTP 클라이언트 (`scraper/http_client.py`) — UA 로테이션, 쓰로틀링, 재시도
- [x] 뉴스 파서 — formula1.com, the-race.com, autosport.com (`scraper/parsers/`)
- [x] 중복 감지 (`scraper/dedup.py`) — URL 정규화 + Jaccard 유사도
- [x] 스크래퍼 서비스 (`scraper/service.py`) — 전체 소스 오케스트레이션
- [x] Next.js 레이아웃, Header, Sidebar, 랜딩 페이지
- [x] Docker Compose, API 클라이언트

### 미구현 컴포넌트
- [ ] FIA 프레스 컨퍼런스 파서
- [ ] 동적 스케줄러
- [ ] LLM 파이프라인
- [ ] REST API 엔드포인트
- [ ] MongoDB/Elasticsearch 스키마 및 인덱스
- [ ] 프론트엔드 데이터 연동 페이지
- [ ] CI/CD

---

## 3. 기술 스택 상세

### Backend
| 패키지 | 버전 | 상태 | 용도 |
|---------|------|------|------|
| FastAPI | >=0.115 | 사용중 | REST API |
| Motor | >=3.6 | 사용중 | MongoDB async |
| elasticsearch[async] | >=8.17 | 사용중 | 검색 |
| Pydantic | >=2.10 | 사용중 | 모델, 스케줄, 기사 |
| pydantic-settings | >=2.7 | 사용중 | 설정 |
| httpx | >=0.28 | 사용중 | 스크래퍼 HTTP 클라이언트 |
| beautifulsoup4 | >=4.12 | 사용중 | HTML 파싱 |
| FastF1 | >=3.4 | 사용중 | 스케줄 조회 |
| uvicorn | >=0.34 | 사용중 | ASGI 서버 |
| APScheduler | >=3.10 | 미사용 | 스케줄링 (Task 1.4) |

### Frontend
| 패키지 | 상태 | 용도 |
|---------|------|------|
| Next.js 15 (16.1.6) | 사용중 | App Router |
| React 19 | 사용중 | UI |
| TypeScript | 사용중 | 타입 시스템 |
| Tailwind CSS v4 | 사용중 | 스타일링 |

---

## 4. 파일 구조

```
f1-insight-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── elasticsearch.py
│   │   ├── models/
│   │   │   ├── schedule.py
│   │   │   └── article.py       # NEW: 뉴스 기사 모델
│   │   ├── services/
│   │   │   ├── schedule.py
│   │   │   ├── fastf1_client.py
│   │   │   └── schedule_data_2026.py
│   │   ├── scraper/
│   │   │   ├── __init__.py      # ScraperService export
│   │   │   ├── http_client.py   # NEW: 비동기 HTTP 클라이언트
│   │   │   ├── dedup.py         # NEW: 중복 감지
│   │   │   ├── service.py       # NEW: 스크래퍼 오케스트레이터
│   │   │   └── parsers/
│   │   │       ├── __init__.py  # NEW: 파서 레지스트리
│   │   │       ├── base.py      # NEW: 추상 파서
│   │   │       ├── formula1.py  # NEW: formula1.com 파서
│   │   │       ├── the_race.py  # NEW: the-race.com 파서
│   │   │       └── autosport.py # NEW: autosport.com 파서
│   │   ├── llm/
│   │   └── scheduler/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/ (unchanged)
├── docs/
├── docker-compose.yml
└── .env.example
```

---

## 5. 이슈 및 개선 사항

### 현재 이슈
- Docker/Python 3.12+/ruff 호스트 미설치
- 파서 CSS 셀렉터는 실제 사이트 HTML 기반 튜닝 필요

### 기술 부채
- CORS `allow_origins=["*"]` 프로덕션 제한 필요
- `_SESSION_DURATIONS` 중복 (fastf1_client.py, schedule.py)
- 파서 셀렉터가 사이트 구조 변경 시 깨질 수 있음 — 모니터링 필요

### 리스크
- 뉴스 사이트 스크래핑 정책(robots.txt, rate limiting) 준수 필요
- 사이트 HTML 구조 변경 시 파서 업데이트 필요

---

## 6. 태스크 완료 로그

| 태스크 | 완료일 | 커밋 | 요약 |
|--------|--------|------|------|
| Task 0.1 | 2026-03-10 | 008f18e | 프로젝트 구조 초기화 |
| Task 0.2 | 2026-03-10 | c677813 | Docker Compose 인프라 |
| Task 0.3 | 2026-03-10 | 1b6bc68 | FastAPI 보일러플레이트 |
| Task 0.4 | 2026-03-10 | cc7ca3a | Next.js 보일러플레이트 |
| Task 1.1 | 2026-03-10 | 4dc404f | FastF1 스케줄 통합 |
| Task 1.2 | 2026-03-10 | (pending) | 뉴스 스크래퍼: 3개 소스 파서, HTTP 클라이언트, 중복 감지, 서비스 오케스트레이터 |

---

## 7. 추후 태스크 제안

- MongoDB 인증 추가 (프로덕션)
- Docker Compose 프로파일 분리
- CORS 프로덕션 강화
- 로깅 모듈화
- 스크래핑 모니터링 대시보드
- robots.txt 파서 통합
- 파서 셀렉터 자동 검증 테스트

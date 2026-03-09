# F1 Insight AI - Project Analysis

> 이 파일은 각 태스크 완료 후 자동으로 업데이트됩니다.
> 프로젝트 현황을 파악하고, 추후 tasks.md에 새 태스크를 추가할 때 참고합니다.

---

## 1. 현재 진행 상황

| Phase | 완료 | 전체 | 진행률 |
|-------|------|------|--------|
| Phase 0: Project Init | 1 | 4 | 25% |
| Phase 1: Data Collection | 0 | 4 | 0% |
| Phase 2: Data Storage | 0 | 3 | 0% |
| Phase 3: LLM Pipeline | 0 | 4 | 0% |
| Phase 4: API & Frontend | 0 | 4 | 0% |
| Phase 5: DevOps | 0 | 4 | 0% |
| Phase 6: YouTube (확장) | 0 | 4 | 0% |
| **전체** | **1** | **27** | **4%** |

**마지막 완료 태스크**: Task 0.1 — 프로젝트 디렉토리 구조 생성
**다음 태스크**: Task 0.2 — Docker Compose 인프라 구성

---

## 2. 아키텍처 현황

### 구현된 컴포넌트
- [x] 프로젝트 디렉토리 구조 (backend/, frontend/, docs/)
- [x] FastAPI 앱 스켈레톤 (`backend/app/main.py` — health check only)
- [x] Next.js 15 앱 스켈레톤 (create-next-app 보일러플레이트)
- [x] Docker Compose 스켈레톤 (MongoDB, ES, backend, frontend 정의)
- [x] pyproject.toml 의존성 정의
- [x] API 클라이언트 유틸리티 (`frontend/src/lib/api.ts`)

### 미구현 컴포넌트
- [ ] MongoDB 연결 모듈 (Motor)
- [ ] Elasticsearch 연결 모듈
- [ ] 스크래퍼 모듈
- [ ] LLM 파이프라인
- [ ] 스케줄러
- [ ] 프론트엔드 레이아웃/페이지
- [ ] REST API 엔드포인트
- [ ] CI/CD

---

## 3. 기술 스택 상세

### Backend
| 패키지 | 버전 | 상태 | 용도 |
|---------|------|------|------|
| FastAPI | >=0.115 | pyproject.toml에 정의 | REST API |
| Motor | >=3.6 | pyproject.toml에 정의, 미연결 | MongoDB async |
| elasticsearch[async] | >=8.17 | pyproject.toml에 정의, 미연결 | 검색 |
| httpx | >=0.28 | pyproject.toml에 정의, 미사용 | HTTP client |
| beautifulsoup4 | >=4.12 | pyproject.toml에 정의, 미사용 | 파싱 |
| APScheduler | >=3.10 | pyproject.toml에 정의, 미사용 | 스케줄링 |
| FastF1 | >=3.4 | pyproject.toml에 정의, 미사용 | F1 데이터 |
| Pydantic | >=2.10 | pyproject.toml에 정의, 미사용 | 모델 |

### Frontend
| 패키지 | 상태 | 용도 |
|---------|------|------|
| Next.js 15 | 설치됨 | 프레임워크 |
| TypeScript | 설치됨 | 타입 시스템 |
| Tailwind CSS v4 | 설치됨 | 스타일링 |

### Infrastructure
| 서비스 | 이미지 | 상태 |
|---------|--------|------|
| MongoDB | mongo:7 | docker-compose 정의됨, 미검증 |
| Elasticsearch | 8.17.0 | docker-compose 정의됨, 미검증 |
| Backend | python:3.12-slim | Dockerfile 있음 |
| Frontend | node:22-alpine | Dockerfile 있음 (multi-stage) |

---

## 4. 파일 구조

```
f1-insight-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 앱 (health check only)
│   │   ├── api/__init__.py      # 라우터 (비어있음)
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
│   │   │   ├── layout.tsx       # 기본 레이아웃 (boilerplate)
│   │   │   ├── page.tsx         # 홈페이지 (boilerplate)
│   │   │   ├── globals.css
│   │   │   └── favicon.ico
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
- 없음 (초기 상태)

### 기술 부채
- `frontend/src/app/page.tsx` — create-next-app 보일러플레이트. Task 4.2에서 교체 예정.
- `frontend/src/app/layout.tsx` — 메타데이터가 "Create Next App"으로 설정됨. Task 0.4에서 수정 필요.

### 리스크
- FastF1 라이브러리가 2026 시즌 데이터를 지원하는지 확인 필요
- Elasticsearch 메모리 설정 (512MB) — Mac Mini 스펙에 따라 조정 필요
- 뉴스 사이트 스크래핑 정책 변경 가능성

---

## 6. 태스크 완료 로그

| 태스크 | 완료일 | 커밋 | 요약 |
|--------|--------|------|------|
| Task 0.1 | 2026-03-10 | 008f18e | 프로젝트 디렉토리 구조, pyproject.toml, docker-compose.yml 스켈레톤, Next.js 초기화 |

---

## 7. 추후 태스크 제안

> 여기에 tasks.md에 추가할 새 태스크 아이디어를 기록합니다.

- (아직 없음)

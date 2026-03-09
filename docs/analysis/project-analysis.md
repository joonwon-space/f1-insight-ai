# F1 Insight AI - Project Analysis

> 이 파일은 각 태스크 완료 후 자동으로 업데이트됩니다.

---

## 1. 현재 진행 상황

| Phase | 완료 | 전체 | 진행률 |
|-------|------|------|--------|
| Phase 0: Project Init | 4 | 4 | 100% |
| Phase 1: Data Collection | 4 | 4 | 100% |
| Phase 2: Data Storage | 0 | 3 | 0% |
| Phase 3: LLM Pipeline | 0 | 4 | 0% |
| Phase 4: API & Frontend | 0 | 4 | 0% |
| Phase 5: DevOps | 0 | 4 | 0% |
| Phase 6: YouTube (확장) | 0 | 4 | 0% |
| **전체** | **8** | **27** | **30%** |

**마지막 완료 태스크**: Task 1.4 — 동적 스케줄러 구현
**다음 태스크**: Task 2.1 — MongoDB 스키마 및 모델 설계
**Phase 1 완료!** Phase 2 (Data Storage) 진입.

---

## 2. 아키텍처 현황

### 구현된 컴포넌트
- [x] FastAPI 앱 — lifespan (DB + 스케줄러), CORS, 라우터
- [x] Core 모듈 — Settings, MongoDB, Elasticsearch 연결
- [x] F1 스케줄 서비스 — FastF1 + 2026 폴백
- [x] 뉴스 스크래퍼 — 3개 소스, HTTP 클라이언트, 중복 감지
- [x] FIA 트랜스크립트 파서 — PDF 다운로드/파싱, 발언자 분리
- [x] 동적 스케줄러 — APScheduler, NORMAL/RACE_WEEKEND 모드 자동 전환
- [x] Next.js 레이아웃, Header, Sidebar, 랜딩 페이지
- [x] Docker Compose, API 클라이언트

### 미구현 컴포넌트
- [ ] MongoDB 스키마/인덱스
- [ ] Elasticsearch 인덱스 매핑
- [ ] MongoDB → ES 동기화
- [ ] LLM 파이프라인
- [ ] REST API 엔드포인트 (news, search, schedule)
- [ ] 프론트엔드 데이터 페이지
- [ ] CI/CD

---

## 3. 기술 스택 상세

### Backend — 모든 패키지 사용중
| 패키지 | 용도 |
|---------|------|
| FastAPI + uvicorn | REST API, ASGI 서버 |
| Motor | MongoDB async |
| elasticsearch[async] | 검색 |
| Pydantic/pydantic-settings | 모델, 설정 |
| httpx | 스크래퍼 HTTP |
| beautifulsoup4 | HTML 파싱 |
| pdfplumber | PDF 텍스트 추출 |
| FastF1 | 스케줄 조회 |
| APScheduler | 동적 스케줄러 |

---

## 4. 파일 구조

```
backend/app/
├── main.py              # lifespan: DB + scheduler
├── api/router.py        # /health, /scheduler/status
├── core/ (config.py, database.py, elasticsearch.py)
├── models/ (schedule.py, article.py, transcript.py)
├── services/ (schedule.py, fastf1_client.py, schedule_data_2026.py)
├── scraper/
│   ├── http_client.py, dedup.py, service.py
│   ├── parsers/ (formula1, the_race, autosport)
│   └── transcript/ (pdf_downloader, pdf_parser, speaker_parser, service)
├── scheduler/
│   ├── __init__.py      # exports
│   ├── models.py        # SchedulerMode, SchedulerStatus
│   └── service.py       # 스케줄러 시작/정지, 모드 전환
└── llm/
```

---

## 5. 이슈 및 개선 사항

### 기술 부채
- `pdf_downloader.py` → ScraperHttpClient 내부 메서드 접근
- speaker_parser 드라이버/팀 데이터 하드코딩 → Task 2.1 후 교체
- `_SESSION_DURATIONS` 중복 (fastf1_client, schedule)
- CORS `allow_origins=["*"]` 프로덕션 제한

### 리스크
- APScheduler 3.x → 4.x 마이그레이션 가능성
- 스크래퍼 파서 CSS 셀렉터 사이트 변경 시 깨짐

---

## 6. 태스크 완료 로그

| 태스크 | 완료일 | 커밋 | 요약 |
|--------|--------|------|------|
| Task 0.1 | 2026-03-10 | 008f18e | 프로젝트 구조 초기화 |
| Task 0.2 | 2026-03-10 | c677813 | Docker Compose 인프라 |
| Task 0.3 | 2026-03-10 | 1b6bc68 | FastAPI 보일러플레이트 |
| Task 0.4 | 2026-03-10 | cc7ca3a | Next.js 보일러플레이트 |
| Task 1.1 | 2026-03-10 | 4dc404f | FastF1 스케줄 통합 |
| Task 1.2 | 2026-03-10 | 4bf6082 | 뉴스 스크래퍼 |
| Task 1.3 | 2026-03-10 | 8786c9c | FIA 트랜스크립트 파서 |
| Task 1.4 | 2026-03-10 | (pending) | 동적 스케줄러 (NORMAL/RACE_WEEKEND 모드, 자동 전환) |

---

## 7. 추후 태스크 제안

- ScraperHttpClient에 `fetch_bytes()` 추가
- FIA 미디어 센터 자동 크롤링
- 스케줄러 모니터링 UI (프론트엔드)
- APScheduler 4.x 마이그레이션 검토

# F1 Insight AI - Project Analysis

> 이 파일은 각 태스크 완료 후 자동으로 업데이트됩니다.

---

## 1. 현재 진행 상황

| Phase | 완료 | 전체 | 진행률 |
|-------|------|------|--------|
| Phase 0: Project Init | 4 | 4 | 100% |
| Phase 1: Data Collection | 3 | 4 | 75% |
| Phase 2: Data Storage | 0 | 3 | 0% |
| Phase 3: LLM Pipeline | 0 | 4 | 0% |
| Phase 4: API & Frontend | 0 | 4 | 0% |
| Phase 5: DevOps | 0 | 4 | 0% |
| Phase 6: YouTube (확장) | 0 | 4 | 0% |
| **전체** | **7** | **27** | **26%** |

**마지막 완료 태스크**: Task 1.3 — FIA 프레스 컨퍼런스 트랜스크립트 파서
**다음 태스크**: Task 1.4 — 동적 스케줄러 구현

---

## 2. 아키텍처 현황

### 구현된 컴포넌트
- [x] FastAPI 앱 — lifespan, CORS, 라우터
- [x] Core 모듈 — Settings, MongoDB, Elasticsearch 연결
- [x] F1 스케줄 서비스 — FastF1 + 2026 폴백
- [x] 뉴스 스크래퍼 — 3개 소스 파서, HTTP 클라이언트, 중복 감지
- [x] FIA 트랜스크립트 파서 — PDF 다운로드, 텍스트 추출, 발언자 분리
- [x] Next.js 레이아웃, Header, Sidebar, 랜딩 페이지
- [x] Docker Compose, API 클라이언트

### 미구현 컴포넌트
- [ ] 동적 스케줄러 (APScheduler)
- [ ] LLM 파이프라인
- [ ] REST API 엔드포인트
- [ ] MongoDB/ES 스키마 및 인덱스
- [ ] 프론트엔드 데이터 연동 페이지
- [ ] CI/CD

---

## 3. 기술 스택 상세

### Backend
| 패키지 | 상태 | 용도 |
|---------|------|------|
| FastAPI | 사용중 | REST API |
| Motor | 사용중 | MongoDB async |
| elasticsearch[async] | 사용중 | 검색 |
| Pydantic/pydantic-settings | 사용중 | 모델, 설정 |
| httpx | 사용중 | 스크래퍼 HTTP |
| beautifulsoup4 | 사용중 | HTML 파싱 |
| pdfplumber | 사용중 | PDF 텍스트 추출 |
| FastF1 | 사용중 | 스케줄 조회 |
| APScheduler | 미사용 | Task 1.4에서 사용 |

---

## 4. 파일 구조

```
backend/app/
├── main.py
├── api/router.py
├── core/ (config.py, database.py, elasticsearch.py)
├── models/
│   ├── schedule.py
│   ├── article.py
│   └── transcript.py       # NEW: 트랜스크립트 모델
├── services/ (schedule.py, fastf1_client.py, schedule_data_2026.py)
├── scraper/
│   ├── http_client.py, dedup.py, service.py
│   ├── parsers/ (formula1, the_race, autosport)
│   └── transcript/          # NEW
│       ├── __init__.py
│       ├── pdf_downloader.py
│       ├── pdf_parser.py
│       ├── speaker_parser.py
│       └── service.py
├── llm/, scheduler/
```

---

## 5. 이슈 및 개선 사항

### 기술 부채
- `pdf_downloader.py`가 `ScraperHttpClient` 내부 메서드 접근 → `fetch_bytes()` 공개 메서드 추가 필요
- speaker_parser의 드라이버/팀 데이터가 하드코딩 → Task 2.1 마스터 데이터로 교체 예정
- FIA 미디어 센터 페이지 크롤러 없음 → URL 직접 제공 필요

---

## 6. 태스크 완료 로그

| 태스크 | 완료일 | 커밋 | 요약 |
|--------|--------|------|------|
| Task 0.1 | 2026-03-10 | 008f18e | 프로젝트 구조 초기화 |
| Task 0.2 | 2026-03-10 | c677813 | Docker Compose 인프라 |
| Task 0.3 | 2026-03-10 | 1b6bc68 | FastAPI 보일러플레이트 |
| Task 0.4 | 2026-03-10 | cc7ca3a | Next.js 보일러플레이트 |
| Task 1.1 | 2026-03-10 | 4dc404f | FastF1 스케줄 통합 |
| Task 1.2 | 2026-03-10 | 4bf6082 | 뉴스 스크래퍼 (3 소스, HTTP, 중복 감지) |
| Task 1.3 | 2026-03-10 | (pending) | FIA 트랜스크립트 파서 (PDF 다운로드/파싱, 발언자 분리) |

---

## 7. 추후 태스크 제안

- ScraperHttpClient에 `fetch_bytes()` 공개 메서드 추가
- FIA 미디어 센터 자동 크롤링 (PDF URL 자동 발견)
- 드라이버/팀 마스터 데이터 통합 (Task 2.1 후)
- 파서 셀렉터 자동 검증 테스트

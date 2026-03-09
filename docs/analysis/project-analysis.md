# F1 Insight AI - Project Analysis

> 이 파일은 각 태스크 완료 후 자동으로 업데이트됩니다.

---

## 1. 현재 진행 상황

| Phase | 완료 | 전체 | 진행률 |
|-------|------|------|--------|
| Phase 0: Project Init | 4 | 4 | 100% |
| Phase 1: Data Collection | 4 | 4 | 100% |
| Phase 2: Data Storage | 1 | 3 | 33% |
| Phase 3: LLM Pipeline | 0 | 4 | 0% |
| Phase 4: API & Frontend | 0 | 4 | 0% |
| Phase 5: DevOps | 0 | 4 | 0% |
| Phase 6: YouTube (확장) | 0 | 4 | 0% |
| **전체** | **9** | **27** | **33%** |

**마지막 완료 태스크**: Task 2.1 — MongoDB 스키마 및 모델 설계
**다음 태스크**: Task 2.2 — Elasticsearch 인덱스 매핑 설계

---

## 2. 아키텍처 현황

### 구현된 컴포넌트
- [x] FastAPI 앱 — lifespan (DB + 스케줄러 + 인덱스 + 마스터데이터)
- [x] Core 모듈 — Settings, MongoDB, Elasticsearch 연결
- [x] F1 스케줄 서비스 — FastF1 + 2026 폴백
- [x] 뉴스 스크래퍼 — 3개 소스, HTTP 클라이언트, 중복 감지
- [x] FIA 트랜스크립트 파서 — PDF 다운로드/파싱, 발언자 분리
- [x] 동적 스케줄러 — NORMAL/RACE_WEEKEND 모드 자동 전환
- [x] MongoDB 스키마 — Team/Driver 모델, 2026 마스터 데이터 (11팀, 22드라이버)
- [x] MongoDB Repository 계층 — Article, Transcript, MasterData CRUD
- [x] MongoDB 인덱스 자동 생성 (startup)
- [x] Next.js 레이아웃, Header, Sidebar, 랜딩 페이지
- [x] Docker Compose, API 클라이언트

### 미구현 컴포넌트
- [ ] Elasticsearch 인덱스 매핑
- [ ] MongoDB → ES 동기화
- [ ] LLM 파이프라인
- [ ] REST API 엔드포인트 (news, search, schedule)
- [ ] 프론트엔드 데이터 페이지
- [ ] CI/CD

---

## 4. 파일 구조 (변경 사항)

```
backend/app/
├── main.py              # lifespan: DB + scheduler + indexes + master data
├── models/
│   ├── schedule.py, article.py, transcript.py
│   ├── team.py          # NEW: Team, Driver 모델
│   └── master_data.py   # NEW: 2026 마스터 데이터 (11팀, 22드라이버)
├── services/
│   ├── repository.py    # NEW: ArticleRepo, TranscriptRepo, MasterDataRepo
│   ├── db_indexes.py    # NEW: MongoDB 인덱스 자동 생성
│   ├── schedule.py, fastf1_client.py, schedule_data_2026.py
├── scraper/, scheduler/, llm/
```

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
| Task 1.4 | 2026-03-10 | 2385793 | 동적 스케줄러 |
| Task 2.1 | 2026-03-10 | (pending) | MongoDB 스키마: Team/Driver 모델, 마스터 데이터, Repository, 인덱스 |

---

## 7. 추후 태스크 제안

- ScraperHttpClient에 `fetch_bytes()` 추가
- speaker_parser를 MasterDataRepository 연동으로 교체
- Cadillac 드라이버 확정 시 master_data 업데이트

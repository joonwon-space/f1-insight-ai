# F1 Insight AI - Project Analysis

> 이 파일은 각 태스크 완료 후 자동으로 업데이트됩니다.

---

## 1. 현재 진행 상황

| Phase | 완료 | 전체 | 진행률 |
|-------|------|------|--------|
| Phase 0: Project Init | 4 | 4 | 100% |
| Phase 1: Data Collection | 4 | 4 | 100% |
| Phase 2: Data Storage | 2 | 3 | 67% |
| Phase 3: LLM Pipeline | 0 | 4 | 0% |
| Phase 4: API & Frontend | 0 | 4 | 0% |
| Phase 5: DevOps | 0 | 4 | 0% |
| Phase 6: YouTube (확장) | 0 | 4 | 0% |
| **전체** | **10** | **27** | **37%** |

**마지막 완료 태스크**: Task 2.2 — Elasticsearch 인덱스 매핑 설계
**다음 태스크**: Task 2.3 — MongoDB → Elasticsearch 동기화 파이프라인

---

## 2. 아키텍처 현황

### 구현된 컴포넌트
- [x] FastAPI 앱 — lifespan (DB + ES + 스케줄러 + 인덱스 + 마스터데이터)
- [x] Core 모듈 — Settings, MongoDB, Elasticsearch 연결
- [x] F1 스케줄 서비스, 뉴스 스크래퍼, FIA 트랜스크립트 파서
- [x] 동적 스케줄러 — NORMAL/RACE_WEEKEND 모드
- [x] MongoDB 스키마 — Team/Driver, 마스터 데이터, Repository, 인덱스
- [x] ES 인덱스 매핑 — f1_articles (EN/KR 다국어, fingerprint dedup)
- [x] ES 검색 서비스 — multi_match, 필터, 부스팅
- [x] ES 인덱서 — 단건/벌크 인덱싱, fingerprint 기반 upsert
- [x] Next.js 레이아웃, Docker Compose

### 미구현 컴포넌트
- [ ] MongoDB → ES 동기화 파이프라인
- [ ] LLM 파이프라인
- [ ] REST API 엔드포인트
- [ ] 프론트엔드 데이터 페이지
- [ ] CI/CD

---

## 4. 파일 구조 (services/ 변경)

```
backend/app/services/
├── schedule.py, fastf1_client.py, schedule_data_2026.py
├── repository.py        # MongoDB CRUD
├── db_indexes.py        # MongoDB 인덱스
├── es_indexes.py        # NEW: ES 인덱스 매핑 (f1_articles)
├── es_indexer.py        # NEW: ES 문서 인덱싱 (fingerprint dedup)
└── es_search.py         # NEW: ES 검색 (multi_match, 필터)
```

---

## 6. 태스크 완료 로그

| 태스크 | 완료일 | 커밋 | 요약 |
|--------|--------|------|------|
| Task 0.1~0.4 | 2026-03-10 | - | Phase 0 완료 |
| Task 1.1~1.4 | 2026-03-10 | - | Phase 1 완료 |
| Task 2.1 | 2026-03-10 | 391f9ee | MongoDB 스키마, 마스터 데이터, Repository |
| Task 2.2 | 2026-03-10 | (pending) | ES 인덱스 매핑, 검색 서비스, 인덱서 |

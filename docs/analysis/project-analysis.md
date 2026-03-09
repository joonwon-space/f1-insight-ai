# F1 Insight AI - Project Analysis

> 이 파일은 각 태스크 완료 후 자동으로 업데이트됩니다.

---

## 1. 현재 진행 상황

| Phase | 완료 | 전체 | 진행률 |
|-------|------|------|--------|
| Phase 0: Project Init | 4 | 4 | 100% |
| Phase 1: Data Collection | 4 | 4 | 100% |
| Phase 2: Data Storage | 3 | 3 | 100% |
| Phase 3: LLM Pipeline | 4 | 4 | 100% |
| Phase 4: API & Frontend | 0 | 4 | 0% |
| Phase 5: DevOps | 0 | 4 | 0% |
| Phase 6: YouTube (확장) | 0 | 4 | 0% |
| **전체** | **15** | **27** | **56%** |

**마지막 완료 태스크**: Task 3.4 — 자동 태깅 시스템
**다음 태스크**: Task 4.1 — REST API 엔드포인트 구현
**Phase 3 완료!** Phase 4 (API & Frontend) 진입.

---

## 2. 아키텍처 현황

### 구현된 컴포넌트
- [x] FastAPI 앱, Core 모듈, Docker Compose
- [x] Phase 1: 스케줄, 스크래퍼, 트랜스크립트, 스케줄러
- [x] Phase 2: MongoDB 스키마/Repository, ES 매핑/검색, 동기화
- [x] Phase 3: LLM 클라이언트 (Ollama/OpenAI), 요약, 번역, 태깅
- [x] API: /health, /scheduler/status, /sync/*, /llm/*, /tags
- [x] Next.js 레이아웃

### 미구현 컴포넌트
- [ ] REST API (news CRUD, search, schedule)
- [ ] 프론트엔드 데이터 페이지 (뉴스 목록/상세, 캘린더)
- [ ] CI/CD

---

## 4. 파일 구조 (llm/ 최종)

```
backend/app/llm/
├── __init__.py
├── models.py            # LLMProvider, LLMRequest, LLMResponse
├── ollama_client.py     # Ollama REST API
├── openai_client.py     # OpenAI-compatible
├── service.py           # 통합 LLM 서비스
├── prompts.py           # 요약/번역 프롬프트
├── summarizer.py        # 영문 요약
├── translator.py        # 한국어 번역
├── glossary.py          # F1 용어집 (EN→KR)
├── tagger.py            # 규칙 기반 자동 태깅
└── pipeline.py          # 요약+번역+태깅 파이프라인 오케스트레이터
```

---

## 6. 태스크 완료 로그

| 태스크 | 완료일 | 요약 |
|--------|--------|------|
| Phase 0 (0.1~0.4) | 2026-03-10 | 프로젝트 구조, Docker, 백엔드/프론트엔드 보일러플레이트 |
| Phase 1 (1.1~1.4) | 2026-03-10 | 스케줄, 스크래퍼, 트랜스크립트, 스케줄러 |
| Phase 2 (2.1~2.3) | 2026-03-10 | MongoDB 스키마, ES 매핑, 동기화 |
| Task 3.1 | 2026-03-10 | Ollama/OpenAI LLM 클라이언트 |
| Task 3.2 | 2026-03-10 | AIDA 영문 요약 파이프라인 |
| Task 3.3 | 2026-03-10 | 한국어 번역 + F1 용어집 |
| Task 3.4 | 2026-03-10 | 규칙 기반 자동 태깅 (팀/드라이버/토픽) |

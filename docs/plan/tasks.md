# F1 Insight AI - Task List

> 각 Phase별로 체크리스트 형태로 관리합니다.
> 완료된 항목은 `- [x]`로 표시합니다.

---

## Phase 0: 환경 셋업 및 프로젝트 초기화

### 0.1 프로젝트 구조 및 개발 환경 ✅
- [x] 프로젝트 디렉토리 구조 재정리 (React + Vite 기반으로 전환)
- [x] `.env.example` 업데이트 (LLM API 키, Unsplash API 키, Cloudflare 설정 추가)
- [x] `.gitignore` 정비 (Vite 빌드 산출물, 캐시 등)
- [x] `CLAUDE.md` 업데이트 (변경된 기술 스택 반영)
- [x] Python `pyproject.toml` 의존성 정리 (`feedparser` 추가, `fastf1` 유지, 불필요 패키지 제거)

### 0.2 Docker Compose 인프라 ✅
- [x] MongoDB 7 컨테이너 설정 (헬스체크, 볼륨, 네트워크)
- [x] Elasticsearch 8 컨테이너 설정 (메모리 제한, JVM 힙, 헬스체크)
- [x] Backend (FastAPI) 서비스 설정
- [x] Frontend (React + Vite) 서비스 설정 — nginx on port 80
- [x] `docker-compose.yml` 통합 검증

### 0.3 Cloudflare Tunnel 설정
- [ ] Cloudflare 계정에 도메인 등록 및 DNS 설정
- [ ] `cloudflared` 설치 및 터널 생성 (`cloudflared tunnel create f1-insight`)
- [ ] `config.yml` 작성 (프론트엔드 → `/`, 백엔드 API → `/api`)
- [ ] 터널 서비스 등록 (Mac Mini 부팅 시 자동 시작)
- [ ] HTTPS 접근 확인 및 SSL 인증서 검증
- [ ] docker-compose에 cloudflared 서비스 추가 (선택)

---

## Phase 1: 백엔드 기반 구축

### 1.1 FastAPI 백엔드 보일러플레이트 ✅
- [x] FastAPI 앱 초기화 (`backend/app/main.py`) — lifespan, CORS
- [x] 라우터 구조 세팅 (`api/`, `models/`, `services/`, `core/`)
- [x] Pydantic Settings 환경 변수 모듈 (`core/config.py`)
- [x] MongoDB 연결 모듈 — Motor async driver (`core/database.py`)
- [x] Elasticsearch 연결 모듈 — async client (`core/elasticsearch.py`)
- [x] 기본 health check 엔드포인트 (`GET /health`)

### 1.2 MongoDB 스키마 및 모델 설계 ✅
- [x] 뉴스 Article 모델: 제목, 본문, 소스, 작성일, 태그, 이미지 URL, 요약(EN/KR)
- [x] 시즌/라운드/세션 계층 구조 메타데이터 모델
- [x] 11개 팀 및 22명 드라이버 마스터 데이터
- [x] Pydantic v2 모델 + Motor ODM 연동
- [x] MongoDB 인덱스 자동 생성 (URL unique, source, tags, published_at)
- [x] Repository 패턴 구현 (ArticleRepository, MasterDataRepository)

### 1.3 Elasticsearch 인덱스 매핑 ✅
- [x] `f1_articles` 인덱스 매핑 (제목/본문 full-text, 팀/드라이버 keyword 필터)
- [x] 한국어/영어 다국어 분석기 설정 (nori 플러그인 폴백)
- [x] 중복 감지용 fingerprint 필드 (SHA-256 해시)
- [x] 인덱스 자동 생성 함수 (`ensure_es_indexes()`)
- [x] ES 검색 서비스 (multi_match, 필터, 부스팅)
- [x] ES 인덱서 (단건/벌크 인덱싱)

### 1.4 MongoDB → Elasticsearch 동기화 ✅
- [x] Change Stream 기반 실시간 동기화 (replica set 필요, 폴백 처리)
- [x] Full Sync (초기 동기화 / 복구용, 배치 100건 단위)
- [x] 동기화 상태 모니터링 엔드포인트 (`GET /sync/status`)
- [x] 에러 핸들링 및 재시도 로직

---

## Phase 2: 데이터 수집 파이프라인

### 2.1 RSS 피드 수집 (1차 데이터 소스) ✅
- [x] `feedparser` 라이브러리 설치 및 RSS 파서 모듈 구현
- [x] F1 공식 RSS 피드 파싱 (`formula1.com/en/latest/all.xml`)
- [x] RSS 항목 → Article 모델 변환 (제목, 링크, 발행일, 요약)
- [x] RSS 기반 중복 감지 (GUID/링크 기반)
- [x] 추가 RSS 소스 확장 가능 구조 (the-race.com, autosport.com RSS 등)

### 2.2 HTML 스크래핑 (2차 보조 수집) ✅
- [x] httpx 비동기 HTTP 클라이언트 (UA 로테이션, 쓰로틀링, 재시도)
- [x] BeautifulSoup 기반 기사 본문 추출 파서
- [x] 대상 소스: formula1.com, the-race.com, autosport.com
- [x] 중복 기사 감지 (URL 정규화 + 제목 Jaccard 유사도)

### 2.3 FastF1 세션 스케줄 통합 ✅
- [x] FastF1 캐시 설정 및 시즌 캘린더 조회
- [x] 세션별 시작/종료 시간 파싱 (FP1-FP3, Qualifying, Sprint, Race)
- [x] 현재 진행 중인 세션 / 다음 세션 판별 유틸리티
- [x] 2026 시즌 폴백 데이터 (FastF1 미지원 시)

### 2.4 동적 스케줄러 ✅
- [x] APScheduler AsyncIOScheduler 설정
- [x] 비경기일: 하루 1~2회 수집 (크론 8AM, 8PM UTC)
- [x] 경기 당일: 15~30분 간격 수집 (인터벌 잡, IP 차단 방지)
- [x] FastF1 세션 스케줄 연동 → 자동 모드 전환 (NORMAL ↔ RACE_WEEKEND)
- [x] 스케줄러 상태 모니터링 엔드포인트 (`GET /scheduler/status`)
- [x] FastAPI lifespan에 스케줄러 시작/정지 통합

---

## Phase 3: LLM 요약 및 번역 파이프라인

### 3.1 LLM API 클라이언트 ✅
- [x] OpenAI API 클라이언트 (GPT-4o / GPT-4o-mini)
- [x] Anthropic API 클라이언트 (Claude Sonnet / Haiku)
- [x] 통합 LLM 서비스 — 프로바이더 추상화, 폴백 로직
- [x] LLM 상태 엔드포인트 (`GET /llm/status`)
- [x] API 키 검증 및 에러 핸들링

### 3.2 영문 요약 생성 ✅
- [x] 기사 본문 → 1문단 영문 요약 프롬프트 설계
- [x] 배치 처리 (asyncio.Semaphore 기반 동시성 제어)
- [x] 요약 품질 검증 (길이, 키워드 포함, 제목 중복 방지)
- [x] 요약 파이프라인 오케스트레이터 (fetch → summarize → save → re-index)
- [x] 수동 트리거 엔드포인트 (`POST /llm/summarize`)

### 3.3 한국어 번역 ✅
- [x] 영문 요약 → 한국어 번역 프롬프트 설계
- [x] F1 전문 용어 일관성 유지 (한영 용어집 기반)
- [x] 번역 품질 검증 (한글 비율, 길이 체크)
- [x] 번역 결과 MongoDB 저장 + ES 인덱스 업데이트
- [x] 수동 트리거 엔드포인트 (`POST /llm/translate`)

### 3.4 자동 태깅 ✅
- [x] 규칙 기반 팀/드라이버 자동 태깅 (정규식 매칭)
- [x] 팀명 에일리어스 처리 (VCARB/Racing Bulls/AlphaTauri 등)
- [x] 세션/토픽 태깅 (qualifying, race, penalty, crash, strategy 등)
- [x] 태그 정규화 및 마스터 데이터 연동
- [x] 태깅 파이프라인 + 수동 트리거 (`POST /llm/tag`)
- [x] 전체 파이프라인 (요약 + 번역 + 태깅) 엔드포인트 (`POST /llm/pipeline`)

---

## Phase 4: REST API 엔드포인트

### 4.1 뉴스 API ✅
- [x] `GET /api/news` — 뉴스 목록 (페이지네이션, 소스/팀/드라이버/태그 필터)
- [x] `GET /api/news/{id}` — 뉴스 상세 (요약 EN/KR + 태그 + 이미지)
- [x] `GET /api/search` — Elasticsearch 기반 전문 검색
- [x] `GET /api/news/tags` — 전체 태그 목록

### 4.2 스케줄 API ✅
- [x] `GET /api/schedule` — 시즌 캘린더 (연도별)
- [x] `GET /api/schedule/current` — 현재/다음 세션 정보
- [x] `GET /api/schedule/{round}` — 특정 라운드 세션 상세

### 4.3 마스터 데이터 API ✅
- [x] `GET /api/teams` — 전체 팀 목록
- [x] `GET /api/drivers` — 전체 드라이버 목록 (팀 필터)

### 4.4 이미지 API ✅
- [x] Unsplash API 연동 모듈
- [x] 뉴스 키워드 기반 관련 이미지 자동 검색
- [ ] 이미지 URL 캐싱 (MongoDB에 저장, 동일 기사 재요청 방지) — Phase 5에서 프론트엔드 통합 시 처리
- [x] `GET /api/images/search?q=...` — 이미지 검색 프록시

---

## Phase 5: React + shadcn/ui 프론트엔드

### 5.1 프로젝트 셋업 ✅
- [x] Vite + React 19 + TypeScript 프로젝트 초기화
- [x] Tailwind CSS v4 설정
- [x] shadcn/ui 설치 및 초기 설정 (수동 컴포넌트: Button, Badge, Card, Skeleton, Sheet, Separator, Input)
- [x] React Router 설정 (SPA 라우팅)
- [x] API 클라이언트 유틸리티 (`lib/api.ts`)
- [x] 환경 변수 설정 (`VITE_API_URL`)

### 5.2 레이아웃 및 공통 컴포넌트 ✅
- [x] 루트 레이아웃 (Header + Sidebar + Main)
- [x] Header — F1 Insight AI 브랜딩, 네비게이션 (News, Schedule, Search)
- [x] Sidebar — 팀/드라이버 필터 (shadcn Accordion, Checkbox)
- [x] 반응형 모바일 레이아웃 (Sheet 사이드바, 햄버거 메뉴)
- [x] 다크 모드 기본 적용 (F1 테마 — 레드 #e10600 액센트)
- [x] 로딩 스켈레톤 (shadcn Skeleton)

### 5.3 뉴스 목록 페이지 ✅
- [x] 뉴스 카드 컴포넌트 (제목, 요약 미리보기, 소스, 날짜, 팀 배지)
- [ ] 레이스 주간별 뉴스 그룹핑 뷰 — 추후 개선
- [x] 팀/드라이버/소스 필터 사이드바 연동
- [x] 무한 스크롤 또는 페이지네이션 (shadcn Pagination)
- [x] Unsplash 이미지 카드에 표시 (image_url 필드 사용)

### 5.4 뉴스 상세 페이지 ✅
- [x] 영문 요약 표시 (상단)
- [x] 한국어 번역 표시 (바로 아래 배치)
- [x] 원문 소스 링크
- [ ] 태그 기반 관련 뉴스 추천 — 추후 개선
- [x] Unsplash 관련 이미지 표시 (image_url 필드 사용)
- [x] 공유 버튼 (URL 복사, SNS)

### 5.5 시즌 캘린더 대시보드 ✅
- [x] 24개 그랑프리 타임라인/캘린더 뷰
- [x] 현재/다음 레이스 하이라이트 (카운트다운)
- [ ] 각 라운드별 뉴스 카운트 표시 — 추후 개선
- [x] 세션 스케줄 (FP, Q, Race) 시간대 표시

### 5.6 검색 페이지 ✅
- [x] 검색 입력 (shadcn Input + Command Palette 스타일)
- [x] 검색 결과 하이라이트
- [x] 팀/드라이버/날짜 필터 조합
- [x] 검색 결과 페이지네이션

---

## Phase 6: DevOps 및 배포

### 6.1 Docker 컨테이너화
- [ ] Backend Dockerfile (Python 3.12-slim, multi-stage)
- [ ] Frontend Dockerfile (Node 22-alpine, Vite 빌드, nginx 서빙)
- [ ] docker-compose.yml 통합 (depends_on + healthcheck)
- [ ] 환경 변수 관리 (.env 연동)

### 6.2 Cloudflare Tunnel 배포
- [ ] 터널 config.yml에 서비스 라우팅 규칙 설정
- [ ] 프론트엔드: `https://도메인/` → frontend 컨테이너
- [ ] 백엔드 API: `https://도메인/api/*` → backend 컨테이너
- [ ] Cloudflare Access 정책 설정 (필요 시 관리자 페이지 보호)
- [ ] 터널 자동 재시작 설정 (launchd 또는 docker restart policy)

### 6.3 CI/CD (GitHub Actions) ✅
- [x] 린트 + 타입 체크 (Ruff, ESLint, tsc)
- [x] 테스트 실행 (pytest, vitest)
- [x] Docker 이미지 빌드 검증
> ⚠️ `.github/workflows/ci.yml` 생성 완료, but push 보류 — `workflow` OAuth scope 필요. `gh auth refresh -h github.com -s workflow` 후 수동 push 필요
- [ ] Mac Mini SSH 배포 자동화 (선택)

### 6.4 모니터링 및 운영
- [ ] 로그 수집 및 구조화 (JSON 로깅)
- [ ] 헬스체크 대시보드 (/health, /scheduler/status, /sync/status, /llm/status)
- [ ] Cloudflare Analytics 연동
- [ ] 에러 알림 (Discord/Slack 웹훅 또는 이메일)

---

## Phase 7: 유튜브 자동화 (장기 플랜)

### 7.1 영상 스크립트 자동 생성
- [ ] 웹 요약 데이터 → 영상 스크립트 변환 프롬프트
- [ ] 3열 테이블 구조 (보이스오버, 장면 묘사, 재생 시간)
- [ ] AIDA 프레임워크 적용 (10초 이내 후킹, 30초마다 전환)
- [ ] SEO 키워드 최적화 (vidIQ 연동 검토)

### 7.2 TTS 음성 합성
- [ ] ElevenLabs API 또는 Edge TTS 연동
- [ ] 음성 프로필 설정 (F1 해설 톤)
- [ ] Speech-to-Speech 감정 합성 (Pro Stack)
- [ ] 오디오 파일 저장 및 관리

### 7.3 비디오 자동 제작
- [ ] FFmpeg 기반 이미지/클립 합성
- [ ] Unsplash/로열티 프리 스톡 영상 소스 연동
- [ ] FastF1 텔레메트리 차트 자동 생성 및 삽입
- [ ] 자막 생성 (SRT/VTT)

### 7.4 YouTube API 자동 업로드
- [ ] YouTube Data API v3 OAuth 인증
- [ ] 영상 업로드 자동화
- [ ] 메타데이터 최적화 (제목, 설명, 태그, 썸네일)
- [ ] Shorts + 롱폼 이중 포맷 관리

### 7.5 성과 분석
- [ ] YouTube Analytics API 연동
- [ ] 조회수/구독자 추이 대시보드
- [ ] 콘텐츠 최적화 피드백 루프

---

## 참고: 2026 시즌 데이터 기준

### 팀 목록 (11개 팀)
| 팀 | 파워 유닛 |
|---|---|
| Mercedes | Mercedes |
| Ferrari | Ferrari |
| McLaren | Mercedes |
| Red Bull | RBPT (Ford) |
| Alpine | Mercedes |
| Williams | Mercedes |
| VCARB (Racing Bulls) | RBPT (Ford) |
| Aston Martin | Honda |
| Haas | Ferrari |
| Audi | Audi |
| Cadillac | TBD |

---

## 사용자 추가 작업

> 아래에 추가 작업 항목을 자유롭게 기록하세요.

- [ ]
- [ ]
- [ ]

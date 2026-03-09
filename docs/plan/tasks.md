# F1 Insight AI - Task List

> Claude Code가 각 Task를 순서대로 작업하고 커밋합니다.
> 각 Task는 하나의 독립적인 커밋 단위입니다.

---

## Phase 0: Project Initialization

### Task 0.1 — 프로젝트 디렉토리 구조 생성 ✅
- `backend/`, `frontend/`, `docker/` 기본 디렉토리 구조 생성
- `.env.example`, `.gitignore`, `README.md` 작성
- Python `pyproject.toml` 또는 `requirements.txt` 초기 설정
- 프로젝트 루트 설정 파일 (`docker-compose.yml` 스켈레톤)

### Task 0.2 — Docker Compose 인프라 구성 ✅
- MongoDB 7.x 컨테이너 설정
- Elasticsearch 8.x 컨테이너 설정 (메모리 제한, JVM 힙 32GB 이하)
- 볼륨 마운트 및 네트워크 구성
- 헬스체크 설정

### Task 0.3 — FastAPI 백엔드 보일러플레이트
- FastAPI 앱 초기화 (`backend/app/main.py`)
- 라우터 구조 세팅 (`api/`, `models/`, `services/`)
- MongoDB 연결 모듈 (Motor async driver)
- Elasticsearch 연결 모듈
- 기본 health check 엔드포인트

### Task 0.4 — Next.js 프론트엔드 보일러플레이트
- Next.js 15 App Router 프로젝트 초기화
- TypeScript + Tailwind CSS 설정
- 기본 레이아웃 컴포넌트 (헤더, 사이드바, 메인 영역)
- API 클라이언트 유틸리티 (`lib/api.ts`)

---

## Phase 1: Data Collection (스크래핑)

### Task 1.1 — FastF1 세션 스케줄 통합
- FastF1 라이브러리 설치 및 캐시 설정 (`fastf1.Cache.enable_cache`)
- 2026 시즌 캘린더 (24개 그랑프리) 조회 모듈
- 세션별 시작/종료 시간 파싱 (FP1-FP3, Qualifying, Sprint, Race)
- 현재 진행 중인 세션/다음 세션 판별 유틸리티

### Task 1.2 — F1 뉴스 스크래퍼 구현
- httpx 비동기 HTTP 클라이언트 설정
- 대상 뉴스 소스 정의 (formula1.com, the-race.com, autosport.com 등)
- BeautifulSoup 기반 기사 본문 추출 파서
- User-Agent 로테이션 및 요청 쓰로틀링
- 중복 기사 감지 로직 (URL 기반 + 제목 유사도)

### Task 1.3 — FIA 프레스 컨퍼런스 트랜스크립트 파서
- FIA 미디어 센터 PDF 다운로드 모듈
- PDF → 텍스트 변환 (pdfplumber 또는 pymupdf)
- 발언자별 텍스트 분리 파싱
- 드라이버/팀 프린시펄별 발언 데이터 구조화

### Task 1.4 — 동적 스케줄러 구현
- APScheduler 설정 (AsyncIOScheduler)
- 기본 크론 잡: 비경기일 1~2회/일 수집
- 레이스 위크엔드 자동 전환: 세션 전후 10분 간격 수집
- FastF1 세션 스케줄 연동으로 자동 빈도 전환
- 스케줄 상태 모니터링 엔드포인트

---

## Phase 2: Data Storage (저장소)

### Task 2.1 — MongoDB 스키마 및 모델 설계
- 뉴스 Article 모델: 제목, 본문, 소스, 작성일, 태그, 이미지 URL
- 트랜스크립트 Transcript 모델: 세션 정보, 발언자, 발언 내용
- 시즌/라운드/세션 계층 구조 메타데이터 모델
- 11개 팀 및 22명 드라이버 마스터 데이터
- Pydantic 모델 + Motor ODM 연동

### Task 2.2 — Elasticsearch 인덱스 매핑 설계
- 뉴스 검색 인덱스: 제목/본문 full-text 검색, 팀/드라이버 필터
- 비정규화된 단일 문서 구조 (nested/parent-child 회피)
- 한국어/영어 다국어 분석기 설정
- 중복 감지용 fingerprint 필드

### Task 2.3 — MongoDB → Elasticsearch 동기화 파이프라인
- MongoDB Change Stream 기반 실시간 동기화
- JSON 평탄화(Flattening) 변환 로직
- 벌크 인덱싱 모듈
- 동기화 실패 재시도 및 에러 핸들링

---

## Phase 3: LLM Pipeline (요약 및 번역)

### Task 3.1 — Ollama 로컬 LLM 통합
- Ollama 서비스 연동 모듈 (REST API 호출)
- 모델 로드 확인 및 헬스체크
- OpenAI-compatible API 래퍼 (로컬/클라우드 LLM 전환 가능)
- 60/40 메모리 규칙 기반 모델 선택 가이드 (7B~8B 4-bit 양자화 권장)

### Task 3.2 — 영문 요약 생성 파이프라인
- 기사 본문 → 1문단 영문 요약 프롬프트 설계
- AIDA 프레임워크 적용 (Attention-Interest-Desire-Action)
- 배치 처리 모듈 (다수 기사 순차/병렬 처리)
- 요약 품질 검증 로직 (길이, 키워드 포함 여부)

### Task 3.3 — 한국어 번역 파이프라인
- 영문 요약 → 한국어 번역 프롬프트 설계
- F1 전문 용어 일관성 유지 (용어집 기반)
- 번역 결과 MongoDB 저장 및 ES 인덱스 업데이트

### Task 3.4 — 자동 태깅 시스템
- 팀/드라이버/세션 자동 태깅 (NER 또는 규칙 기반)
- 태그 정규화 (팀명 변경 반영: VCARB, Cadillac 등 11개 팀)
- 태그 기반 Elasticsearch 필터 쿼리

---

## Phase 4: API 및 Frontend

### Task 4.1 — REST API 엔드포인트 구현
- `GET /api/news` — 뉴스 목록 (페이지네이션, 필터)
- `GET /api/news/{id}` — 뉴스 상세 (요약 + 번역 포함)
- `GET /api/schedule` — 시즌 캘린더 및 세션 정보
- `GET /api/search` — Elasticsearch 기반 전문 검색
- `GET /api/teams`, `GET /api/drivers` — 마스터 데이터

### Task 4.2 — 프론트엔드 뉴스 목록 페이지
- 레이스 위크엔드별 뉴스 그룹핑 뷰
- 팀/드라이버 필터 사이드바
- 무한 스크롤 또는 페이지네이션
- 반응형 카드 레이아웃

### Task 4.3 — 프론트엔드 뉴스 상세 페이지
- 영문 요약 + 한국어 번역 토글 표시
- 원문 소스 링크
- 관련 뉴스 추천
- 태그 기반 네비게이션

### Task 4.4 — 시즌 캘린더 대시보드
- 24개 그랑프리 타임라인/캘린더 뷰
- 현재/다음 레이스 하이라이트
- 각 라운드별 뉴스 카운트 표시
- 세션 스케줄 (FP, Q, Race) 시간대 표시

---

## Phase 5: DevOps & Deployment

### Task 5.1 — Backend Dockerfile 및 서비스 통합
- Python 백엔드 Dockerfile 작성
- docker-compose.yml에 backend 서비스 추가
- 환경 변수 관리 (.env 연동)
- 서비스 간 의존성 설정 (depends_on + healthcheck)

### Task 5.2 — Frontend Dockerfile 및 서비스 통합
- Next.js 프로덕션 빌드 Dockerfile
- docker-compose.yml에 frontend 서비스 추가
- 빌드 최적화 (multi-stage build)

### Task 5.3 — Reverse Proxy 및 SSL 설정
- Caddy 또는 Nginx 설정
- HTTPS 자동 인증서 (Let's Encrypt)
- API 라우팅 (`/api/*` → backend, `/*` → frontend)
- Rate limiting 설정

### Task 5.4 — GitHub Actions CI/CD
- 린트 + 타입 체크 (Python: ruff, Frontend: eslint + tsc)
- 테스트 실행 (pytest, vitest)
- Docker 이미지 빌드 검증
- 배포 자동화 (Mac Mini SSH deploy)

---

## Phase 6: YouTube Automation (Phase 2 확장)

### Task 6.1 — 영상 스크립트 자동 생성
- 웹 요약 데이터 → 영상 스크립트 변환 프롬프트
- 3열 테이블 구조 (보이스오버, 장면 묘사, 재생 시간)
- AIDA 프레임워크 적용 (10초 이내 후킹, 30초마다 전환)
- SEO 키워드 최적화 (vidIQ 연동 검토)

### Task 6.2 — TTS 음성 합성 통합
- ElevenLabs API 또는 Edge TTS 연동
- 음성 프로필 설정 (F1 해설 톤)
- Speech-to-Speech 감정 합성 (Pro Stack)
- 오디오 파일 저장 및 관리

### Task 6.3 — 비디오 자동 제작 파이프라인
- FFmpeg 기반 이미지/클립 합성
- 로열티 프리 스톡 영상 소스 연동 (Coverr 등)
- FastF1 텔레메트리 차트 자동 생성 및 삽입
- 자막 생성 (SRT/VTT)

### Task 6.4 — YouTube API 자동 업로드
- YouTube Data API v3 OAuth 인증
- 영상 업로드 자동화
- 메타데이터 최적화 (제목, 설명, 태그, 썸네일)
- Shorts + 롱폼 이중 포맷 관리

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

### 2026 주요 규정 변화 요약
- 파워 유닛: ICE 400kW + MGU-K 350kW (50:50 에너지 분배)
- MGU-H 폐지, 랩당 에너지 회수 8.5MJ
- 능동형 공기역학 (Active Aero): DRS 폐지, X-모드/Z-모드 실시간 전환
- 오버테이크 모드: 1초 이내 간격 시 350kW 추가 전력 수동 전개
- 차량 경량화: 최소 중량 770kg, 휠베이스 3400mm
- 100% 지속가능 연료 의무 사용

# F1 Insight AI - Project Overview

## 1. 프로젝트 개요

### 비전
F1 그랑프리(프랙티스, 퀄리파잉, 레이스) 전후로 공식 RSS 피드 및 뉴스를 자동 수집하고, LLM API로 영문 요약 + 한국어 번역을 생성하여 웹페이지로 제공한다.

### 비즈니스 모델
1. **Phase 1 (MVP)**: F1 뉴스 수집 → LLM 요약/번역 → 웹 서비스
2. **Phase 2 (확장)**: 웹 데이터 기반 유튜브 쇼츠/영상 자동 제작 → 수익화

---

## 2. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Mac Mini (Local Server)                       │
│                                                                     │
│  ┌─────────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐ │
│  │ RSS/Scraper │───▶│  MongoDB  │───▶│  LLM API  │───▶│  React   │ │
│  │ (Collector) │    │ (Raw Data)│    │ (OpenAI/  │    │  + shad  │ │
│  │             │    │           │    │  Claude)  │    │  cn/ui   │ │
│  └─────────────┘    └─────┬─────┘    └───────────┘    └──────────┘ │
│                           │                                         │
│                           ▼                                         │
│                    ┌──────────────┐         ┌──────────────────┐    │
│                    │Elasticsearch │         │  Unsplash API    │    │
│                    │(Search Index)│         │ (Copyright-free) │    │
│                    └──────────────┘         └──────────────────┘    │
│                                                                     │
│  ┌──────────────────┐                ┌──────────────────────────┐   │
│  │   APScheduler    │                │   Cloudflare Tunnel      │   │
│  │ (Dynamic Cron)   │                │ (SSL + Domain Routing)   │   │
│  └──────────────────┘                └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │   cloudflare.com     │
                    │ f1insight.example.com│
                    │  (외부 도메인 접근)    │
                    └──────────────────────┘
```

### 인프라 구성

| 구분 | 기술 | 비고 |
|------|------|------|
| 하드웨어 | Mac Mini | 서버, DB, 웹 호스팅 모두 로컬 구동 |
| 컨테이너 | Docker Compose | MongoDB, Elasticsearch, Backend, Frontend |
| 네트워크 | Cloudflare Tunnel | 포트포워딩 없이 외부 도메인 연결 + 자동 SSL |
| 도메인 | Cloudflare DNS | HTTPS 적용, DDoS 방어 |

---

## 3. 기술 스택

### Backend
| 기술 | 용도 |
|------|------|
| Python 3.12+ | API 서버, 스크래핑, LLM 파이프라인 |
| FastAPI | REST API 프레임워크 |
| APScheduler | 동적 크론 스케줄링 |
| feedparser | RSS 피드 파싱 (1차 데이터 수집) |
| httpx + BeautifulSoup | HTML 스크래핑 (2차 보조 수집) |
| FastF1 | 세션 스케줄 감지, 경기일 판별 |

### Database
| 기술 | 용도 |
|------|------|
| MongoDB 7 | 원천 데이터 및 메타데이터 저장 (스크래핑 결과, 기사 본문) |
| Elasticsearch 8 | 빠른 텍스트 검색, AI 처리를 위한 색인, 중복 감지 |

### LLM
| 기술 | 용도 |
|------|------|
| OpenAI API (GPT-4o) | 영문 요약 생성, 한국어 번역 |
| Anthropic API (Claude) | 대체/보조 LLM 프로바이더 |

> Ollama 로컬 LLM은 사용하지 않고, 외부 LLM API만 사용한다.

### Frontend
| 기술 | 용도 |
|------|------|
| React 19 | SPA 프론트엔드 |
| shadcn/ui | UI 컴포넌트 라이브러리 |
| Tailwind CSS | 스타일링 |
| TypeScript | 타입 안전성 |
| Vite | 빌드 도구 |

### DevOps
| 기술 | 용도 |
|------|------|
| Docker Compose | 서비스 오케스트레이션 |
| Cloudflare Tunnel | 외부 접근, SSL, 도메인 라우팅 |
| GitHub Actions | CI/CD (린트, 테스트, 빌드 검증) |

---

## 4. 데이터 파이프라인

### 4.1 End-to-End 흐름

```
[1] 수집 (Collection)
     │
     │  1차: F1 공식 RSS 피드 (formula1.com/en/latest/all.xml)
     │  2차: 뉴스 사이트 HTML 스크래핑 (the-race.com, autosport.com 등)
     │  세션 스케줄: FastF1 연동으로 경기일 판별
     │
     ▼
[2] 저장 (Storage)
     │
     │  MongoDB: 원천 데이터 저장 (제목, 본문, 소스, 날짜, 태그)
     │  Elasticsearch: 검색 인덱스 동기화
     │
     ▼
[3] 처리 (LLM Processing)
     │
     │  외부 LLM API 호출 (OpenAI / Claude)
     │  → 영문 1문단 요약 생성
     │  → 한국어 번역 생성
     │  → 팀/드라이버/세션 자동 태깅
     │
     ▼
[4] 제공 (Delivery)
     │
     │  React + shadcn/ui 웹페이지
     │  → 레이스 주간별 뉴스 분류
     │  → 11개 팀별 / 22명 드라이버별 필터
     │  → 영문 요약 + 한국어 번역 병렬 표시
     │  → Unsplash API 기반 관련 이미지 제공
     └
```

### 4.2 수집 스케줄링

| 상황 | 수집 주기 | 트리거 |
|------|----------|--------|
| 비경기일 (프랙티스/레이스 없는 날) | 하루 1~2회 | 기본 크론 |
| 경기 당일 (레이스 주간) | 15분~30분 간격 | FastF1 세션 스케줄 기반 자동 전환 |

- IP 차단 방지를 위해 경기 당일에도 15분 이상 간격 유지
- RSS 피드 우선 사용으로 서버 부하 최소화

### 4.3 데이터 분류 체계

```
Season 2026
 └── Round 01: Bahrain GP
      ├── FP1 / FP2 / FP3
      ├── Qualifying
      ├── Sprint (해당 시)
      ├── Race
      └── News / Interviews
           ├── By Team (11개 팀)
           │    ├── Mercedes, Ferrari, McLaren, Red Bull
           │    ├── Alpine, Williams, VCARB (Racing Bulls)
           │    ├── Aston Martin, Haas, Audi, Cadillac
           └── By Driver (22명)
```

### 4.4 LLM 요약 출력 형식

```
[Title] Max Verstappen: "We need to find more pace"
[Source] formula1.com | 2026-03-15 14:30 UTC
[Tags] #RedBull #Verstappen #BahrainGP #Qualifying

[EN Summary]
Verstappen expressed concerns about the car's pace during
qualifying, noting that the team needs to improve rear stability
to compete with McLaren and Ferrari in the race.

[KR 번역]
페르스타펜은 퀄리파잉에서 차량 페이스에 대한 우려를 표했으며,
레이스에서 맥라렌, 페라리와 경쟁하기 위해 리어 안정성을
개선해야 한다고 언급했다.

[Image] Unsplash (copyright-free)
```

### 4.5 미디어 통합

- **Unsplash API**: 저작권 무료 이미지 제공
- 뉴스 내용과 관련된 F1/모터스포츠 이미지 자동 매칭
- 추후 유튜브 상업적 수익화 시 저작권 문제 없음

---

## 5. 유튜브 자동화 파이프라인 (Phase 2 확장)

```
[웹 데이터]
     │
     ▼
[스크립트 생성]  ──▶  LLM이 요약 데이터 기반 영상 스크립트 작성
     │
     ▼
[음성 합성]      ──▶  TTS (ElevenLabs / Edge TTS)
     │
     ▼
[영상 편집]      ──▶  FFmpeg + Unsplash/스톡 영상 합성
     │
     ▼
[업로드]         ──▶  YouTube Data API v3 자동 업로드
     │
     ▼
[수익화]         ──▶  Shorts + 롱폼 이중 포맷
```

| 단계 | 설명 | 우선순위 |
|------|------|---------|
| Step 1 | 웹 요약 → 영상 스크립트 자동 생성 | 높음 |
| Step 2 | TTS 음성 합성 + 자막 생성 | 높음 |
| Step 3 | FFmpeg 이미지/영상 편집 자동화 | 중간 |
| Step 4 | YouTube API 업로드 + 메타데이터 최적화 | 중간 |
| Step 5 | 성과 분석 + 콘텐츠 최적화 피드백 루프 | 낮음 |

---

## 6. 프로젝트 디렉토리 구조

```
f1-insight-ai/
├── docs/
│   ├── plan/
│   │   ├── project-overview.md   # 이 파일
│   │   └── tasks.md              # 세부 작업 목록
│   └── analysis/
│       └── project-analysis.md   # 프로젝트 진행 분석
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI 라우터
│   │   ├── core/                 # 설정, DB 연결
│   │   ├── scraper/              # RSS 파서 + 뉴스 스크래퍼
│   │   ├── scheduler/            # 동적 스케줄러
│   │   ├── llm/                  # LLM 요약/번역 파이프라인
│   │   ├── models/               # Pydantic 모델 + MongoDB 스키마
│   │   └── services/             # 비즈니스 로직, Repository
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/           # shadcn/ui 기반 컴포넌트
│   │   ├── pages/                # 라우트 페이지
│   │   ├── lib/                  # API 클라이언트, 유틸리티
│   │   └── hooks/                # 커스텀 React 훅
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── CLAUDE.md
└── README.md
```

---

## 7. 주요 리스크 및 대응

| 리스크 | 대응 방안 |
|--------|----------|
| RSS 피드 구조 변경 | 다중 소스 대응, 스크래핑 폴백 |
| 뉴스 사이트 IP 차단 | RSS 우선 사용, 15분 이상 간격, UA 로테이션 |
| LLM API 비용 증가 | 요약 대상 필터링, 배치 처리, 캐싱 |
| LLM 요약 품질 편차 | 프롬프트 튜닝, 품질 검증 로직, 프로바이더 폴백 |
| Mac Mini 성능 한계 | ES 메모리 튜닝, MongoDB 인덱스 최적화, 리소스 제한 |
| 유튜브 저작권 이슈 | Unsplash (저작권 프리) 이미지만 사용, 변환적 사용 |
| Cloudflare Tunnel 장애 | 로컬 접근 폴백, 모니터링 알림 |

---

## 8. 2026 시즌 참고 데이터

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

### 2026 주요 규정 변화
- 파워 유닛: ICE 400kW + MGU-K 350kW (50:50 에너지 분배)
- MGU-H 폐지, 랩당 에너지 회수 8.5MJ
- 능동형 공기역학 (Active Aero): DRS 폐지, X-모드/Z-모드 실시간 전환
- 오버테이크 모드: 1초 이내 간격 시 350kW 추가 전력 수동 전개
- 차량 경량화: 최소 중량 770kg, 휠베이스 3400mm
- 100% 지속가능 연료 의무 사용

# F1 Insight AI - Project Overview

## 1. Background

Formula 1 generates a massive volume of news and interviews around every Grand Prix weekend, spanning practice sessions (FP1-FP3), qualifying (Q1-Q3), sprints, and races. Korean-speaking fans struggle to access this information quickly and in a well-organized format.

**F1 Insight AI** solves this problem by automatically collecting F1-related news and interviews, summarizing and translating them via LLM, and delivering the results through a web interface.

## 2. Project Goals

### Phase 1 (MVP)
- Collect F1 news and interviews as **fast as possible** before and after each Grand Prix
- Auto-generate English summaries + Korean translations using LLM
- Serve organized content through a web application

### Phase 2 (Expansion)
- Automatically produce YouTube Shorts/videos from collected and summarized web data
- Build a content monetization business model

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Mac Mini (Local Server)                    │
│                                                                 │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌────────┐ │
│  │  Scraper   │───▶│  MongoDB  │───▶│    LLM    │───▶│  Web   │ │
│  │(Collector) │    │ (Raw Data)│    │(Summary/  │    │(Front- │ │
│  │           │    │           │    │ Translate) │    │ end)   │ │
│  └───────────┘    └─────┬─────┘    └───────────┘    └────────┘ │
│                         │                                       │
│                         ▼                                       │
│                  ┌──────────────┐                                │
│                  │Elasticsearch │                                │
│                  │(Search Index)│                                │
│                  └──────────────┘                                │
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │   Scheduler       │    │  Getty Images    │                   │
│  │(Dynamic Cron)     │    │ (Media Source)   │                   │
│  └──────────────────┘    └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### Infrastructure
| Component | Configuration |
|-----------|---------------|
| Hardware | Mac Mini (server, DB, web hosting all running locally) |
| OS | macOS |
| Containers | Docker Compose (MongoDB, Elasticsearch, etc.) |
| Reverse Proxy | Nginx or Caddy (HTTPS, domain routing) |

---

## 4. Tech Stack

### Backend
| Area | Technology | Purpose |
|------|------------|---------|
| Language | Python 3.12+ | Scraping, LLM pipeline, API server |
| Web Framework | FastAPI | REST API server |
| Scheduler | APScheduler | Dynamic cron scheduling |
| F1 Data | FastF1 | Session schedule detection, telemetry reference |
| Scraping | httpx + BeautifulSoup / Playwright | News and interview collection |

### Database
| Technology | Purpose |
|------------|---------|
| MongoDB | Raw unstructured data and metadata storage |
| Elasticsearch | Text search, LLM processing index, duplicate detection |

### LLM
| Option | Description |
|--------|-------------|
| Local LLM | Ollama (Llama 3, Mistral, etc.) - cost-effective, offline capable |
| API LLM | Claude API / OpenAI API - for high-quality summaries when needed |

### Frontend
| Technology | Purpose |
|------------|---------|
| Next.js (React) | SSR/SSG-based web frontend |
| Tailwind CSS | UI styling |
| TypeScript | Type safety |

### DevOps
| Technology | Purpose |
|------------|---------|
| Docker Compose | Service orchestration |
| GitHub Actions | CI/CD |
| Nginx / Caddy | Reverse proxy, SSL |

---

## 5. Data Pipeline

### 5.1 End-to-End Flow

```
[1] Collection (Scraping)
     │
     │  Check session schedule via FastF1
     │  Crawl news sites / official F1 site / social media
     │  Fetch Getty Images media
     │
     ▼
[2] Storage (DB Ingestion)
     │
     │  MongoDB: Store raw text, metadata (source, timestamp, tags)
     │  Elasticsearch: Sync search index
     │
     ▼
[3] Processing (LLM Summary & Translation)
     │
     │  Generate 1-paragraph English summary
     │  Generate Korean translation
     │  Tag by team / driver / session
     │
     ▼
[4] Delivery (Frontend)
     │
     │  Display summary + translation + images on web page
     │  Filter by race weekend / team / driver
     └
```

### 5.2 Collection Scheduling

| Condition | Frequency | Trigger |
|-----------|-----------|---------|
| Off-race days | 1-2 times per day | Default cron |
| Race weekend (race day) | Every 10 minutes | Dynamic switch based on FastF1 session schedule |

The scheduler automatically switches collection frequency by reading the season calendar and session start/end times from FastF1.

### 5.3 Data Classification

```
Season 2025
 └── Round 01: Bahrain GP
      ├── FP1 / FP2 / FP3
      ├── Qualifying
      ├── Race
      └── News / Interviews
           ├── By Team (11 teams)
           │    ├── Red Bull Racing
           │    ├── McLaren
           │    ├── Ferrari
           │    ├── Mercedes
           │    ├── Aston Martin
           │    ├── Alpine
           │    ├── Williams
           │    ├── RB (Visa Cash App)
           │    ├── Kick Sauber
           │    ├── Haas
           │    └── Cadillac
           └── By Driver (22 drivers)
```

### 5.4 LLM Summary Output Format

Each news/interview item is processed into the following format:

```
[Title] Max Verstappen: "We need to find more pace"
[Source] formula1.com | 2025-03-15 14:30 UTC
[Tags] #RedBull #Verstappen #BahrainGP #Qualifying

[EN Summary]
Verstappen expressed concerns about the car's pace during
qualifying, noting that the team needs to improve rear stability
to compete with McLaren and Ferrari in the race.

[KR Summary]
페르스타펜은 퀄리파잉에서 차량 페이스에 대한 우려를 표했으며,
레이스에서 맥라렌, 페라리와 경쟁하기 위해 리어 안정성을
개선해야 한다고 언급했다.

[Image] Getty Images Embed
```

### 5.5 Media Integration

- **Getty Images Embed**: Utilize the free embed feature with no copyright concerns
- Auto-match relevant F1 images to news content
- Embed codes are inserted directly into the frontend, minimizing copyright risk

---

## 6. YouTube Automation Pipeline (Phase 2 Expansion)

```
[Web Data]
     │
     ▼
[Script Generation]  ──▶  LLM writes video script from summary data
     │
     ▼
[Voice Synthesis]    ──▶  TTS (ElevenLabs / Edge TTS, etc.)
     │
     ▼
[Video Editing]      ──▶  Auto video production (FFmpeg + image/clip compositing)
     │
     ▼
[Upload]             ──▶  Auto upload via YouTube Data API
     │
     ▼
[Monetization]       ──▶  YouTube Shorts + long-form content revenue model
```

### Phased Rollout Plan

| Phase | Description | Priority |
|-------|-------------|----------|
| Phase 1 | Web summary data → Auto video script generation | High |
| Phase 2 | TTS voice synthesis + subtitle generation | High |
| Phase 3 | Auto image/video source editing (FFmpeg) | Medium |
| Phase 4 | YouTube API auto upload + metadata optimization | Medium |
| Phase 5 | Performance analytics + content optimization feedback loop | Low |

---

## 7. Project Directory Structure (Planned)

```
f1-insight-ai/
├── docs/
│   └── plan/
│       └── 프로젝트-개요.md
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routers
│   │   ├── scraper/        # News scraping modules
│   │   ├── scheduler/      # Dynamic scheduler
│   │   ├── llm/            # LLM summary/translation pipeline
│   │   ├── models/         # MongoDB schemas
│   │   └── services/       # Business logic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js App Router
│   │   ├── components/     # UI components
│   │   └── lib/            # Utilities, API client
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 8. Key Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| News site scraping blocks | User-Agent rotation, request throttling, prioritize RSS feeds |
| LLM summary quality variance | Prompt tuning, hybrid local/API LLM usage, summary quality validation pipeline |
| Mac Mini performance limits | Elasticsearch memory tuning, MongoDB index optimization, per-service resource limits |
| Getty Images policy changes | Secure alternative media sources (Unsplash, Wikimedia, etc.) |
| Copyright issues (YouTube videos) | Transformative use of original news, custom graphics, legal review |

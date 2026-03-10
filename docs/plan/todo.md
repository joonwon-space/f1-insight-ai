# F1 Insight AI — 남은 작업 목록

> tasks.md 기준 미완료 항목만 추린 실행 목록입니다.
> 완료 시 `- [x]`로 체크하고, tasks.md에도 반영하세요.
>
> 최종 업데이트: 2026-03-10

---

## 즉시 실행 가능 (인프라 계정 불필요)

### [ ] 4.4 이미지 URL 캐싱
- 동일 기사 재요청 시 MongoDB에 캐시된 이미지 URL 재사용
- `ArticleRepository`에 image_url 저장 로직 추가
- Unsplash API 호출 횟수 절감

### [ ] 5.3 레이스 주간별 뉴스 그룹핑 뷰
- 뉴스 목록 페이지에서 레이스 이벤트 기준으로 그룹핑
- 예: "Round 3 — Australian GP" 섹션 헤더 + 해당 기간 뉴스

### [ ] 5.4 태그 기반 관련 뉴스 추천
- 뉴스 상세 페이지 하단에 같은 팀/드라이버 태그 뉴스 표시
- `GET /api/news?tags=...` 필터 활용

### [ ] 5.5 라운드별 뉴스 카운트 표시
- 시즌 캘린더 각 라운드에 관련 뉴스 수 배지 표시
- 클릭 시 해당 라운드 뉴스 필터링

---

## Cloudflare 계정 필요

### [ ] 0.3 Cloudflare Tunnel 설정 (Mac Mini 운영 전 필수)
- [ ] Cloudflare 계정에 도메인 등록 및 DNS 설정
- [ ] `cloudflared` 설치 및 터널 생성 (`cloudflared tunnel create f1-insight`)
- [ ] `config.yml` 작성 (프론트엔드 → `/`, 백엔드 API → `/api`)
- [ ] 터널 서비스 등록 (Mac Mini 부팅 시 자동 시작)
- [ ] HTTPS 접근 확인 및 SSL 인증서 검증
- [ ] docker-compose에 cloudflared 서비스 추가 (선택)

### [ ] 6.2 Cloudflare Tunnel 배포
- [ ] 터널 config.yml에 서비스 라우팅 규칙 설정
- [ ] 프론트엔드: `https://도메인/` → frontend 컨테이너
- [ ] 백엔드 API: `https://도메인/api/*` → backend 컨테이너
- [ ] Cloudflare Access 정책 설정 (필요 시 관리자 페이지 보호)
- [ ] 터널 자동 재시작 설정 (launchd 또는 docker restart policy)

---

## GitHub Actions (workflow scope 필요)

### [ ] 6.3 CI/CD push 완료
- `gh auth refresh -h github.com -s workflow` 실행 후 push
- 이미 `.github/workflows/ci.yml` 생성됨, push만 하면 됨

### [ ] 6.3 Mac Mini SSH 배포 자동화 (선택)
- GitHub Actions → SSH → Mac Mini 배포 스크립트
- `docker compose pull && docker compose up -d`

---

## Phase 7: YouTube 자동화 (장기)

### [ ] 7.1 영상 스크립트 자동 생성
- 웹 요약 데이터 → 영상 스크립트 변환 프롬프트
- 3열 테이블 구조 (보이스오버, 장면 묘사, 재생 시간)
- AIDA 프레임워크 적용
- SEO 키워드 최적화 (vidIQ 연동 검토)

### [ ] 7.2 TTS 음성 합성
- ElevenLabs API 또는 Edge TTS 연동
- 음성 프로필 설정 (F1 해설 톤)
- 오디오 파일 저장 및 관리

### [ ] 7.3 비디오 자동 제작
- FFmpeg 기반 이미지/클립 합성
- Unsplash/로열티 프리 스톡 영상 소스 연동
- FastF1 텔레메트리 차트 자동 생성 및 삽입
- 자막 생성 (SRT/VTT)

### [ ] 7.4 YouTube API 자동 업로드
- YouTube Data API v3 OAuth 인증
- 영상 업로드 자동화
- 메타데이터 최적화 (제목, 설명, 태그, 썸네일)
- Shorts + 롱폼 이중 포맷 관리

### [ ] 7.5 성과 분석
- YouTube Analytics API 연동
- 조회수/구독자 추이 대시보드
- 콘텐츠 최적화 피드백 루프

---

## 스킵 (외부 의존성 or 불필요)
- 6.4 Cloudflare Analytics 연동 — 외부 계정 필요, 스킵

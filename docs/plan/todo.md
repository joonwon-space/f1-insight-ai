# F1 Insight AI — 수동 작업 목록

> Claude가 대신 할 수 없는 작업들입니다. (계정/인증/외부 서비스)
> 완료 시 `- [x]`로 체크하세요.
>
> 최종 업데이트: 2026-03-10

---

## GitHub — workflow scope 권한

### [x] GitHub Actions CI/CD push
`.github/workflows/ci.yml`은 이미 만들어져 있음. push만 하면 됨.

```bash
gh auth refresh -h github.com -s workflow
git push
```

---

## 외부 접속 (필요할 때)

### [ ] 외부 접속 설정 — 스킵 (로컬만 사용)
로컬 네트워크에서는 `http://Mac-Mini-IP:80` 으로 바로 접속 가능.
외부 접속이 필요해지면 **Tailscale** 사용 (도메인 불필요, 무료):
```bash
brew install tailscale
# Mac Mini + 접속 기기 둘 다 설치 후 같은 계정 로그인
```

---

## YouTube 스크립트 자동 생성 (Phase 7, 장기)

> TTS/영상 제작/업로드는 스킵. 스크립트 생성까지만.

### [ ] 7.1 영상 스크립트 자동 생성
- F1 뉴스 요약 → LLM으로 유튜브 스크립트 변환
- 구성: 보이스오버 + 장면 묘사 + 재생 시간 (3열 구조)
- AIDA 프레임워크 (10초 후킹, 30초마다 전환)
- 결과물을 MongoDB에 저장 + API 엔드포인트 제공

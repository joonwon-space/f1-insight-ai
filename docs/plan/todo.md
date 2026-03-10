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

## YouTube — API 키 및 계정 연동 (Phase 7, 장기)

### [ ] 7.2 ElevenLabs TTS API 키 발급
- https://elevenlabs.io 가입 → API 키 → `.env`에 `ELEVENLABS_API_KEY` 추가

### [ ] 7.4 YouTube Data API 인증
- Google Cloud Console에서 프로젝트 생성
- YouTube Data API v3 활성화
- OAuth 2.0 클라이언트 ID 발급 → `credentials.json` 저장

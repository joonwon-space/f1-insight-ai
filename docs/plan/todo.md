# F1 Insight AI — 수동 작업 목록

> Claude가 대신 할 수 없는 작업들입니다. (계정/인증/외부 서비스)
> 완료 시 `- [x]`로 체크하세요.
>
> 최종 업데이트: 2026-03-10

---

## GitHub — workflow scope 권한

### [ ] GitHub Actions CI/CD push
`.github/workflows/ci.yml`은 이미 만들어져 있음. push만 하면 됨.

```bash
gh auth refresh -h github.com -s workflow
git push
```

---

## Cloudflare — 계정 및 도메인 설정

### [ ] 0.3 / 6.2 Cloudflare Tunnel 설정 및 배포
Mac Mini를 외부에 공개하려면 필요.

1. Cloudflare 계정에 도메인 등록 및 DNS 설정
2. Mac Mini에 `cloudflared` 설치
   ```bash
   brew install cloudflared
   cloudflared tunnel login
   cloudflared tunnel create f1-insight
   ```
3. `~/.cloudflared/config.yml` 작성
   ```yaml
   tunnel: <TUNNEL_ID>
   credentials-file: ~/.cloudflared/<TUNNEL_ID>.json
   ingress:
     - hostname: yourdomain.com
       service: http://localhost:80        # frontend
     - hostname: api.yourdomain.com
       service: http://localhost:8000      # backend
     - service: http_status:404
   ```
4. 터널 서비스 등록 (Mac Mini 부팅 시 자동 시작)
   ```bash
   sudo cloudflared service install
   ```
5. HTTPS 접근 확인 및 SSL 인증서 검증

---

## YouTube — API 키 및 계정 연동 (Phase 7, 장기)

### [ ] 7.2 ElevenLabs TTS API 키 발급
- https://elevenlabs.io 가입 → API 키 → `.env`에 `ELEVENLABS_API_KEY` 추가

### [ ] 7.4 YouTube Data API 인증
- Google Cloud Console에서 프로젝트 생성
- YouTube Data API v3 활성화
- OAuth 2.0 클라이언트 ID 발급 → `credentials.json` 저장

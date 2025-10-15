# gateway

## 환경 설정

### 1. `.env` 파일 생성
```bash
# .env
LG_API_KEY=your_lg_api_key_here
LG_PAT_TOKEN=your_lg_pat_token_here
```

### 1. Docker로 실행
```bash
# 빌드
docker build -t gazehome-gateway .

# 실행
docker run -d \
  --name gateway-docker \
  -p 8001:8001 \
  --env-file .env \
  gateway
```

### 2. 일반 실행 (Docker 없이)
```bash
# 의존성 설치
pip install -r requirements.txt

# 실행
uvicorn main:app --host 0.0.0.0 --port 8001
```

## API 엔드포인트

- `GET /health` - 헬스 체크
- `GET /api/lg/devices` - LG 기기 목록 조회
- `POST /api/lg/control` - LG 기기 제어

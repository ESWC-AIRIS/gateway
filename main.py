"""
GazeHome Gateway Server (간단 버전)
라즈베리파이 ↔ AI Service ↔ LG ThinQ 중간 다리
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from lg_client import get_lg_devices, control_lg_device, get_device_profile, get_device_state, get_device_status
from action_mapper import action_to_command

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GazeHome Gateway")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 설정
AI_SERVICE_URL = "http://localhost:8000"  # AI Service
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"


@app.get("/")
async def root():
    """기본 정보"""
    return {
        "service": "GazeHome Gateway Server",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "healthy"}


# LG ThinQ API 엔드포인트
@app.get("/api/lg/devices")
async def list_lg_devices():
    """LG 기기 목록 조회"""
    try:
        result = await get_lg_devices()
        return result
    except Exception as e:
        logger.error(f"LG 기기 목록 조회 실패: {e}")
        return {"error": str(e)}

@app.get("/api/lg/devices/{device_id}/profile")
async def get_lg_device_profile(device_id: str):
    """LG 기기 프로필 조회"""
    try:
        result = await get_device_profile(device_id)
        return result
    except Exception as e:
        logger.error(f"LG 기기 프로필 조회 실패: {e}")
        return {"error": str(e)}

if DEBUG_MODE:
    @app.get("/api/lg/devices/{device_id}/state")
    async def get_lg_device_state(device_id: str):
        """기기 현재 상태 조회 (debug mode)"""
        try:
            result = await get_device_state(device_id)
            return result
        except Exception as e:
            logger.error(f"LG 기기 현재 상태 조회 실패: {e}")
            return {"error": str(e)}

@app.get("/api/lg/devices/{device_id}/status")
async def get_simple_device_status(device_id: str, device_name: str = None):
    """기기 상태 간단 요약 (ON/OFF, 온도 등)"""
    try:
        result = await get_device_status(device_id, device_name)
        return result
    except Exception as e:
        logger.error(f"간단 상태 조회 실패: {e}")
        return {"error": str(e)}

@app.post("/api/lg/control")
async def control_lg_device_endpoint(data: dict):
    """LG 기기 제어"""
    try:
        device_id = data.get("device_id")
        action = data.get("action")

        if not device_id or not action:
            return {"error": "device_id and action required"}

        # 공기청정기 바람 세기 명령은 AUTO 모드에서 작동 안 하므로 먼저 CLEAN 모드로 변경
        if action.startswith("wind_") and action != "wind_auto":
            logger.info(f"바람 세기 변경 요청: {action} - 먼저 CLEAN 모드로 전환")
            clean_command = {"airPurifierJobMode": {"currentJobMode": "CLEAN"}}
            await control_lg_device(device_id, clean_command)
            # 모드 변경 후 잠시 대기
            import asyncio
            await asyncio.sleep(0.5)

        # 액션을 LG 명령어로 변환
        try:
            command = action_to_command(action)
        except ValueError as e:
            return {"error": str(e)}

        # LG API 호출
        result = await control_lg_device(device_id, command)
        return result

    except Exception as e:
        logger.error(f"간단 제어 실패: {e}")
        return {"error": str(e)}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
    
    
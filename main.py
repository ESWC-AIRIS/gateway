"""
GazeHome Gateway Server (간단 버전)
라즈베리파이 ↔ AI Service ↔ LG ThinQ 중간 다리
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import logging
from datetime import datetime
from lg_client import get_lg_devices, control_lg_device, get_device_profile

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
    
# @app.get("/api/lg/devices/{device_id}/state")
# async def get_lg_device_state(device_id: str):
#     """기기 현재 상태 조회"""
#     try:
#         result = await get_device_state(device_id)
#         return result
#     except Exception as e:
#         logger.error(f"LG 기기 현재 상태 조회 실패: {e}")
#         return {"error": str(e)}

@app.post("/api/lg/control")
async def control_lg_device_endpoint(data: dict):
    """LG 기기 제어"""
    try:
        device_id = data.get("device_id")
        action = data.get("action")

        if not device_id or not action:
            return {"error": "device_id and action required"}

        # 액션을 LG 명령어로 변환
        command = None

        # 공기청정기
        if action == "clean":
            command = {
                "airPurifierJobMode": {
                    "currentJobMode": "CLEAN"}}
        elif action == "auto":
            command = {
                "airPurifierJobMode": {
                    "currentJobMode": "AUTO"
                    }
                }
        elif action == "turn_on":
            command = {
                "airPurifierOperation": {
                    "airPurifierOperationMode": "POWER_ON"
                    }
                }
        elif action == "turn_off":
            command = {
                "airPurifierOperation": {
                    "airPurifierOperationMode": "POWER_OFF"
                    }
                }

        # 건조기
        elif action == "dryer_on":
            command = {
                "operation": {
                    "dryerOperationMode": "POWER_ON"
                }
            }
        elif action == "dryer_off":
            command = {
                "operation": {
                    "dryerOperationMode": "POWER_OFF"
                }
            }
        elif action == "dryer_start":
            command = {
                "operation": {
                    "dryerOperationMode": "START"
                }
            }
        elif action == "dryer_stop":
            command = {
                "operation": {
                    "dryerOperationMode": "STOP"
                }
            }
            
        # 에어컨
        elif action == "aircon_on":
            command = {
                "operation":{
                    "airConOperationMode": "POWER_ON"
                }
            }
        elif action == "aircon_off":
            command = {
                "operation": {
                    "airConOperationMode": "POWER_OFF"
                }
            }
        elif action.startswith("temp_"):
            temp = float(action.split("_")[1])
            command = {
                "temperature": {
                    "targetTemperature": temp
                }
            }
        else:
            return {"error": f"Unknown action: {action}"}

        result = await control_lg_device(device_id, command)
        return result

    except Exception as e:
        logger.error(f"간단 제어 실패: {e}")
        return {"error": str(e)}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
    
    
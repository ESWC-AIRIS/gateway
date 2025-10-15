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
from lg_client import get_lg_devices, control_lg_device

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



# ============================================================
# LG ThinQ API 엔드포인트
# ============================================================
@app.get("/api/lg/devices")
async def list_lg_devices():
    """LG 기기 목록 조회"""
    try:
        result = await get_lg_devices()
        return result
    except Exception as e:
        logger.error(f"LG 기기 목록 조회 실패: {e}")
        return {"error": str(e)}

@app.post("/api/lg/control")
async def control_lg_device_endpoint(data: dict):
    """LG 기기 제어"""
    try:
        device_id = data.get("device_id")
        command = data.get("command")
        
        if not device_id or not command:
            return {"error": "device_id and command required"}
        
        result = await control_lg_device(device_id, command)
        return result
    except Exception as e:
        logger.error(f"LG 기기 제어 실패: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)


# # ============================================================
# # 1️⃣ WebSocket: 라즈베리파이 ↔ Gateway
# # ============================================================
# @app.websocket("/ws/device/{device_id}")
# async def websocket_endpoint(websocket: WebSocket, device_id: str):
#     """
#     라즈베리파이와 WebSocket 연결
    
#     플로우:
#     1. 라즈베리파이 연결
#     2. 클릭 이벤트 받기
#     3. AI Service에 추천 요청
#     4. 추천 결과 라즈베리파이로 전송
#     5. (선택) LG ThinQ 제어
#     """
#     # 연결 수락
#     await websocket.accept()
#     logger.info(f"✅ 라즈베리파이 연결됨: {device_id}")
    
#     try:
#         while True:
#             # 1. 라즈베리파이에서 데이터 받기
#             data = await websocket.receive_json()
#             logger.info(f"📥 라즈베리파이 → Gateway: {data.get('clicked_device', {}).get('device_name')}")
            
#             # 2. AI Service에 추천 요청
#             ai_recommendation = await call_ai_service(data)
#             logger.info(f"🤖 AI 추천 받음: {ai_recommendation.get('recommendation', {}).get('intent')}")
            
#             # 3. 추천을 라즈베리파이로 전송
#             await websocket.send_json({
#                 "type": "ai_recommendation",
#                 "data": ai_recommendation
#             })
#             logger.info(f"📤 Gateway → 라즈베리파이: 추천 전송 완료")
            
#             # 4. (선택) 사용자가 수락하면 LG ThinQ 제어
#             if data.get("user_accepted"):
#                 logger.info("👍 사용자 수락 → LG 기기 제어")
#                 lg_result = await control_lg_device(
#                     ai_recommendation.get('recommendation', {}).get('action')
#                 )
#                 await websocket.send_json({
#                     "type": "lg_control_result",
#                     "data": lg_result
#                 })
    
#     except WebSocketDisconnect:
#         logger.info(f"❌ 연결 종료: {device_id}")
#     except Exception as e:
#         logger.error(f"⚠️ 오류 발생: {e}")


# # ============================================================
# # 2️⃣ HTTP: Gateway → AI Service (아스트라)
# # ============================================================
# async def call_ai_service(data: dict) -> dict:
#     """
#     AI Service에 HTTP POST 요청
    
#     Args:
#         data: 라즈베리파이에서 받은 클릭 이벤트
    
#     Returns:
#         AI 추천 결과
#     """
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"{AI_SERVICE_URL}/api/gaze/click",
#                 json=data,
#                 timeout=30.0
#             )
#             response.raise_for_status()
#             return response.json()
    
#     except httpx.TimeoutException:
#         logger.error("⏱️ AI Service 타임아웃")
#         return {"error": "AI Service timeout"}
#     except Exception as e:
#         logger.error(f"⚠️ AI Service 호출 실패: {e}")
#         return {"error": str(e)}


# # ============================================================
# # 테스트용 엔드포인트
# # ============================================================
# @app.post("/test/ai")
# async def test_ai_service(data: dict):
#     """AI Service 호출 테스트"""
#     result = await call_ai_service(data)
#     return result

import logging
import json

import httpx
import base64
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


# LG ThinQ Connect 설정
LG_API_KEY = os.getenv("LG_API_KEY")
LG_PAT_TOKEN = os.getenv("LG_PAT_TOKEN") 
LG_BASE_URL = "https://api-kic.lgthinq.com"

def generate_message_id() -> str:
    """x-message-id 생성 (22자)"""
    message_id = "yogyui_thing_api_tester"
    message_id_encoded = base64.urlsafe_b64encode(
        bytes(message_id, "UTF-8")
    )
    return message_id_encoded.decode()[:22]

def generate_api_header() -> dict:
    """LG API 공통 헤더 생성"""
    return {
        "Authorization": f"Bearer {LG_PAT_TOKEN}",
        "x-message-id": generate_message_id(),
        "x-country": "KR",
        "x-client-id": "gazehome-gateway",
        "x-api-key": LG_API_KEY
    }


async def get_lg_devices():
    """LG 디바이스 목록 조회"""
    
    if not LG_PAT_TOKEN:
        return {"error": "LG_PAT_TOKEN not configured"}
    
    headers = generate_api_header()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LG_BASE_URL}/devices",
                headers=headers,
                timeout=30.0
            )
            
            logger.info(f"\n{'='*60}")
            logger.info(f"상태 코드: {response.status_code}")
            logger.info(f"응답 내용:")
            logger.info(response.text[:500])
            logger.info(f"{'='*60}\n")    
            
            
            response.raise_for_status()
            return response.json()
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP 에러: {e.response.status_code}")
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 에러: {e}")
        return {"error": f"JSON 파싱 실패: {response.text[:200]}"}
    
    except Exception as e:
        logger.error(f"기타 에러: {str(e)}")
        return {"error": str(e)}


async def control_lg_device(device_id: str, command: dict):
    """LG 디바이스 제어"""
    
    if not LG_PAT_TOKEN:
        return {"error": "LG_PAT_TOKEN not configured"}
    
    headers = generate_api_header() 
    
    print(f"\n{'='*60}")
    print(f"LG API 요청:")
    print(f"URL: {LG_BASE_URL}/devices/{device_id}/control")
    print(f"Headers: {headers}")
    print(f"Command (payload): {command}")
    print(f"{'='*60}\n")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LG_BASE_URL}/devices/{device_id}/control",
                headers=headers,
                json=command,
                timeout=30.0
            )
            

            # ========== 응답 확인 ==========
            logger.info(f"\n{'='*60}")
            logger.info(f"LG API 응답:")
            logger.info(f"상태: {response.status_code}")
            logger.info(f"응답: {response.text[:500]}")
            logger.info(f"{'='*60}\n")
            
            response.raise_for_status()
            return response.json()
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP 에러: {e.response.status_code}")
        logger.error(f"응답 본문: {e.response.text}")
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    
    except Exception as e:
        logger.error(f"제어 실패: {e}")
        return {"error": str(e)}
    

async def get_device_profile(device_id: str):
    """기기 프로필 조회"""
    
    if not LG_PAT_TOKEN:
        return {"error": "LG_PAT_TOKEN not configured"}
    
    headers = generate_api_header()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LG_BASE_URL}/devices/{device_id}/profile",
                headers=headers,
                timeout=30.0
            )
            
            response.raise_for_status()
            return response.json()
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP 에러: {e.response.status_code}")
        logger.error(f"응답 본문: {e.response.text}")
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    
    except Exception as e:
        logger.error(f"기타 에러: {str(e)}")
        return {"error": str(e)}
    

async def get_device_state(device_id: str):
    """기기 현재 상태 조회"""    
    if not LG_PAT_TOKEN:
        return {"error": "LG_PAT_TOKEN not configured"}
    
    headers = generate_api_header()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LG_BASE_URL}/devices/{device_id}/state",
                headers=headers,
                timeout=30.0
            )
            
            response.raise_for_status()
            return response.json()
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP 에러: {e.response.status_code}")
        logger.error(f"응답 본문: {e.response.text}")
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    
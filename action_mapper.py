"""
액션 → LG API 명령어 매핑 테이블
"""

ACTION_MAP = {
    ##### 공기청정기
    ## 모드
    "clean": {"airPurifierJobMode": {"currentJobMode": "CLEAN"}},
    "auto": {"airPurifierJobMode": {"currentJobMode": "AUTO"}},
    "circulator": {"airPurifierJobMode": {"currentJobMode": "CIRCULATOR"}},

    ## 전원
    "purifier_on": {"operation": {"airPurifierOperationMode": "POWER_ON"}},
    "purifier_off": {"operation": {"airPurifierOperationMode": "POWER_OFF"}},

    ## 바람 세기
    "wind_low": {"airFlow": {"windStrength": "LOW"}},
    "wind_mid": {"airFlow": {"windStrength": "MID"}},
    "wind_high": {"airFlow": {"windStrength": "HIGH"}},
    "wind_auto": {"airFlow": {"windStrength": "AUTO"}},
    "wind_power": {"airFlow": {"windStrength": "POWER"}},


    ##### 건조기
    "dryer_on": {"operation": {"dryerOperationMode": "POWER_ON"}},
    "dryer_off": {"operation": {"dryerOperationMode": "POWER_OFF"}},
    "dryer_start": {"operation": {"dryerOperationMode": "START"}},
    "dryer_stop": {"operation": {"dryerOperationMode": "STOP"}},

    ##### 에어컨
    ## 전원
    "aircon_on": {"operation": {"airConOperationMode": "POWER_ON"}},
    "aircon_off": {"operation": {"airConOperationMode": "POWER_OFF"}},

    ## 모드
    "aircon_cool": {"airConJobMode": {"currentJobMode": "COOL"}},
    "aircon_dry": {"airConJobMode": {"currentJobMode": "AIR_DRY"}},
    "aircon_clean": {"airConJobMode": {"currentJobMode": "AIR_CLEAN"}},

    ## 바람 세기
    "aircon_wind_low": {"airFlow": {"windStrength": "LOW"}},
    "aircon_wind_mid": {"airFlow": {"windStrength": "MID"}},
    "aircon_wind_high": {"airFlow": {"windStrength": "HIGH"}},
    "aircon_wind_auto": {"airFlow": {"windStrength": "AUTO"}},
}


def action_to_command(action: str) -> dict:
    # 정적 매핑 확인
    if action in ACTION_MAP:
        return ACTION_MAP[action]

    # 에어컨 온도 설정
    if action.startswith("temp_"):
        try:
            temp = float(action.split("_")[1])  # "temp_25"
            return {"temperature": {"targetTemperature": temp}}
        except (IndexError, ValueError) as e:
            raise ValueError(f"유효하지 않은 온도 포맷입니다. 'temp_숫자' 형식으로 입력하세요. (예: temp_25)")

    # 알 수 없는 액션
    raise ValueError(f"Unknown action: {action}")

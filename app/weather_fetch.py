import os
import re

import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz

kst = pytz.timezone('Asia/Seoul')

load_dotenv()
SERVICE_KEY = os.getenv("SERVICE_KEY")
NX = 62
NY = 128

def get_base_time() -> str:
    now = datetime.now(kst)
    hour = now.hour if now.minute > 45 else now.hour - 1
    return f"{hour:02d}30"

def get_base_date() -> str:
    now = datetime.now(kst)
    if now.hour == 0 and now.minute < 45:
        yesterday = now - timedelta(days=1)
        return f"{yesterday.year}{yesterday.month:02d}{yesterday.day:02d}"
    return f"{now.year}{now.month:02d}{now.day:02d}"

def format_hour(hour: int) -> str:
    period = "오전" if hour < 12 else "오후"
    hour12 = 12 if hour % 12 == 0 else hour % 12
    return f"{period} {hour12}시"

def fetch_weather_json():
    base_time = get_base_time()
    base_date = get_base_date()

    url = (
        f"https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
        f"?serviceKey={SERVICE_KEY}"
        f"&pageNo=1&numOfRows=60&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}"
        f"&nx={NX}&ny={NY}"
    )

    response = requests.get(url)
    if response.status_code != 200:
        return {"error": f"API 요청 실패: {response.status_code}"}

    items = response.json()['response']['body']['items']['item']

    # 시간별 데이터 정리
    weather_by_time = {}
    for item in items:
        time = item['fcstTime']
        category = item['category']
        value = item['fcstValue']
        if time not in weather_by_time:
            weather_by_time[time] = {}
        weather_by_time[time][category] = value

    # 현재 시각 기준으로 4시간치 반환
    now = datetime.now(kst)
    now_hour = now.hour
    result = []
    for i in range(1, 5):
        hour_str = f"{(now_hour + i) % 24:02d}00"
        data = weather_by_time.get(hour_str, {})
        display_hour = format_hour(now_hour + i - 1)

        # 시간 문자열 예: '오전 5시', '오후 3시'
        hour_str = display_hour  # 예: '오전 5시'
        match = re.search(r'오전|오후\s*(\d+)시', hour_str)

        if match:
            am_pm = '오전' if '오전' in hour_str else '오후'
            hour = int(re.search(r'(\d+)시', hour_str).group(1))

            # 오전 5시~오후 8시 => 낮
            if (am_pm == '오전' and hour >= 5) or (am_pm == '오후' and hour <= 8):
                is_night = False  # 낮
            else:
                is_night = True  # 밤
        else:
            is_night = True  # 시간 정보 없으면 기본 밤

        # 하늘 상태
        sky_dict = {'1': '맑음', '3': '구름많음', '4': '흐림'}
        sky = sky_dict.get(data.get('SKY', '1'), '정보없음')

        # 기온
        tmp = data.get('T1H', '0')

        # 습도
        reh = data.get('REH', '0')

        # 강수량
        pcp = data.get('RN1', '강수없음')

        # 풍속
        wind = data.get('WSD', '없음')

        if wind == '없음':
            wind_status = '정보 없음'
        else:
            wind_value = float(wind)  # 문자열이면 float으로 변환
            if wind_value >= 9:
                wind_status = '강한 바람'
            elif wind_value >= 4:
                wind_status = '약간 강한 바람'
            else:
                wind_status = '약한 바람'

        # 하늘 상태 + 시간 -> 기본 코드
        sky_code_map = {
            ('맑음', True): 1,
            ('맑음', False): 2,
            ('구름많음', True): 3,
            ('구름많음', False): 4,
            ('흐림', True): 5,
            ('흐림', False): 6
        }

        # PTY 처리
        pty_code_map = {
            '0': None,
            '1': '비', '4': '비', '5': '비',
            '2': '비+눈', '6': '비+눈',
            '3': '눈', '7': '눈'
        }
        pty = pty_code_map.get(data.get('PTY', '0'))

        # 최종 코드 결정
        if pty:
            pty_number_map = {'비': 7, '비+눈': 8, '눈': 9}
            final_code = pty_number_map[pty]
        else:
            final_code = sky_code_map.get((sky, is_night), 0)

        result.append({
            "time": display_hour,
            "sky": sky,
            "temp": tmp,
            "humidity": reh,
            "precipitation_type": pty if pty else '없음',
            "precipitation_amount": pcp,
            "sky_code": final_code,
            "wind": wind_status
        })

    return result


if __name__ == "__main__":
    import json
    weather_data = fetch_weather_json()
    print(json.dumps(weather_data, ensure_ascii=False, indent=2))

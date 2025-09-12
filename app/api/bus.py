import os
from dotenv import load_dotenv
import requests
import xmltodict
from datetime import datetime, timedelta
import re

load_dotenv()
SERVICE_KEY = os.getenv("SERVICE_KEY")

crowd_map = {
    "0": "데이터없음",
    "3": "여유",
    "4": "보통",
    "5": "혼잡",
}


def get_bus_arrival():
    url = f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={SERVICE_KEY}&stId=106000201&busRouteId=100100178&ord=25"

    response = requests.get(url)
    if response.status_code != 200:
        return {"error": f"API 요청 실패: {response.status_code}"}

    data_dict = xmltodict.parse(response.text)
    item_list = data_dict.get("ServiceResult").get("msgBody").get("itemList")

    # JSON 반환용 리스트
    buses = []
    for i in range(1, 3):  # 1번, 2번 버스
        bus_info = {
            "arrival_time": item_list[f"arrmsg{i}"],
            "bus_no": item_list[f"plainNo{i}"],
            "crowd_code": item_list[f"rerdie_Div{i}"],
            "crowd_level": item_list[f"reride_Num{i}"],
        }
        buses.append(format_bus_info_json(bus_info))

    return buses


def format_bus_info_json(bus):
    arrival_msg = bus["arrival_time"]
    bus_no = bus["bus_no"]
    crowd_code = bus["crowd_code"]
    crowd_level = bus["crowd_level"]

    # 혼잡도 처리
    crowd_str = ""
    if crowd_code == "4":
        crowd_str = crowd_map.get(crowd_level, "")

    # 기본 초기값
    position_str = None

    # "12분22초 후[2번째 전]" 형태 분리
    match_position = re.match(r"([\d분초\s]+).*?\[(.+)\]", arrival_msg)
    if match_position:
        eta_raw = match_position.group(1).strip()  # "12분22초"
        position_str = match_position.group(2).strip()  # "2번째 전"
    else:
        eta_raw = arrival_msg

    # eta 계산
    if eta_raw in ["출발대기"]:
        eta_str = "출발 대기"
        arrival_time = None
    elif eta_raw in ["곧 도착"]:
        eta_str = "곧 도착"
        arrival_time = datetime.now().strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
    else:
        match = re.search(r"(\d+)분(\d+)초", eta_raw)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            arrival_time_dt = datetime.now() + timedelta(minutes=minutes, seconds=seconds)
            eta_str = f"{minutes}분 {seconds}초"
            arrival_time = arrival_time_dt.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
        else:
            eta_str = eta_raw
            arrival_time = datetime.now().strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")

    return {
        "bus_no": bus_no,
        "eta": eta_str,
        "arrival_time": arrival_time,
        "crowd": crowd_str,
        "position": position_str
    }


if __name__ == "__main__":
    import json
    result = get_bus_arrival()
    print(json.dumps(result, ensure_ascii=False, indent=2))

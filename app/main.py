# main.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
from .bus import get_bus_arrival
from .weather_fetch import fetch_weather_json
import logging

logger = logging.getLogger("uvicorn.error")

# 메모리 캐시
cache = {}
BUS_CACHE_EXPIRATION = 5      # 버스 5초
WEATHER_CACHE_EXPIRATION = 300  # 날씨 5분

app = FastAPI(title="CommuteMate API")

# 허용할 프론트엔드 주소
origins = [
    "http://localhost:3000",  # Next.js 개발 서버
    "https://commute.yuruppang.store"  # 운영 url
]

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=origins,      # 허용할 출처
    allow_credentials=True,     # 쿠키 인증 허용 여부
    allow_methods=["*"],        # 허용할 HTTP 메서드 (GET, POST 등)
    allow_headers=["*"],        # 허용할 헤더
)


@app.get("/api/info")
def bus_info():
    try:
        result = {
            "bus": get_cached_data("bus", get_bus_arrival, BUS_CACHE_EXPIRATION),
            "weather": get_cached_data("weather", fetch_weather_json, WEATHER_CACHE_EXPIRATION),
        }
        return JSONResponse(content=result)
    except Exception as e:
        error_content = {"error": str(e)}

        # 로그에 오류 응답 내용 기록
        logger.error("응답 내용: %s", error_content)

        return JSONResponse(content=error_content, status_code=500)


def get_cached_data(key, fetch_func, expiration):
    now = time.time()
    if key in cache:
        data, timestamp = cache[key]
        if now - timestamp < expiration:
            return data
    data = fetch_func()
    cache[key] = (data, now)
    return data

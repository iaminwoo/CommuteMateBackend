# main.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
from .bus import get_bus_arrival
from .weather_fetch import fetch_weather_json

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
        return JSONResponse(content={"error": str(e)}, status_code=500)


def get_cached_data(key, fetch_func, expiration):
    now = time.time()
    if key in cache:
        data, timestamp = cache[key]
        if now - timestamp < expiration:
            return data
    data = fetch_func()
    cache[key] = (data, now)
    return data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

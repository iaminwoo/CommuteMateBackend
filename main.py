# main.py
from fastapi.responses import JSONResponse
import time
from bus import get_bus_arrival
from record_bus import init_csv, record_bus_info
from weather_fetch import fetch_weather_json
import logging
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
import models
from database import engine
from routers import employees, dayoffs, positions
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("uvicorn.error")
kst = pytz.timezone('Asia/Seoul')
scheduler = BackgroundScheduler(timezone=kst)

# 메모리 캐시
cache = {}
BUS_CACHE_EXPIRATION = 5      # 버스 5초
WEATHER_CACHE_EXPIRATION = 300  # 날씨 5분

models.Base.metadata.create_all(bind=engine)

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


@app.on_event("startup")
def startup_event():
    init_csv()
    start_scheduler()


def start_scheduler():
    def schedule_interval_job():
        now = datetime.now(kst)
        start_time = now.replace(hour=4, minute=50, second=0, microsecond=0)
        end_time = now.replace(hour=5, minute=10, second=0, microsecond=0)

        # interval job 등록
        scheduler.add_job(
            func=record_bus_info,
            trigger="interval",
            seconds=15,
            start_date=start_time,
            end_date=end_time,
            id="record_bus_job",
            replace_existing=True
        )
        logger.info("Interval job registered for today: %s ~ %s", start_time, end_time)

    scheduler.add_job(
        func=schedule_interval_job,
        trigger="cron",
        hour=4,
        minute=50,
        id="daily_scheduler_job",
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started with daily cron job")

app.include_router(employees.router)
app.include_router(dayoffs.router)
app.include_router(positions.router)

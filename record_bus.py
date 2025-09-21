import csv
import os
from datetime import datetime
import pytz

from bus import get_bus_arrival

DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

CSV_FILE = os.path.join(DATA_DIR, "bus_data.csv")

kst = pytz.timezone('Asia/Seoul')


def init_csv():
    try:
        with open(CSV_FILE, "x", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["recorded_at", "eta", "expected_arrival", "remaining_stops"])
    except FileExistsError:
        # 이미 파일이 있으면 무시
        pass


def record_bus_info():
    try:
        buses = get_bus_arrival()

        first_bus = buses[0]

        minutes_to_arrival = first_bus.get("eta")
        expected_arrival = first_bus.get("arrival_time")
        remaining_stops = first_bus.get("position")

        now = datetime.now(kst)

        # CSV에 기록
        with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([now.isoformat(), minutes_to_arrival, expected_arrival, remaining_stops])

    except Exception as e:
        print("Error recording bus info:", e)


if __name__ == "__main__":
    init_csv()
    record_bus_info()
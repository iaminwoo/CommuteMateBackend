from collections import defaultdict
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import calendar
from datetime import date, timedelta


def get_employee_dayoffs_by_month(db: Session, year: int, month: int, employee_id: int):
    dayoffs = db.query(models.DayOff).filter(
        models.DayOff.employee_id == employee_id,
        func.strftime("%Y", models.DayOff.date) == str(year),
        func.strftime("%m", models.DayOff.date) == f"{month:02d}"
    ).order_by(models.DayOff.order).all()

    dates = [d.date.isoformat() for d in dayoffs]

    return {
        "employee_id": employee_id,
        "year": year,
        "month": month,
        "dates": dates
    }


def upsert_employee_month_dayoffs(db: Session, employee_id: int, dates: list, year: int, month: int):
    # 기존 데이터 조회
    existing = db.query(models.DayOff).filter(
        models.DayOff.employee_id == employee_id,
        func.strftime("%Y", models.DayOff.date) == str(year),
        func.strftime("%m", models.DayOff.date) == f"{month:02d}"
    ).all()

    existing_map = {d.date.isoformat(): d for d in existing}

    for day_date, dayoff_obj in existing_map.items():
        if day_date not in dates:
            db.delete(dayoff_obj)

    # 날짜 정렬 후 순서(order) 부여
    sorted_dates = sorted(dates)
    for idx, day_date in enumerate(sorted_dates, start=1):
        if day_date in existing_map:
            # update
            existing_map[day_date].order = idx
        else:
            # create
            new_dayoff = models.DayOff(
                employee_id=employee_id,
                date=day_date,
                order=idx
            )
            db.add(new_dayoff)

    db.commit()


def get_dayoffs_by_month(db: Session, year: int, month: int):
    results = (
        db.query(
            models.DayOff.employee_id,
            models.Employee.name,
            models.Employee.order.label("employee_order"),
            models.DayOff.date,
            models.DayOff.order,
        )
        .join(models.Employee, models.Employee.id == models.DayOff.employee_id)  # type: ignore
        .filter(
            func.strftime("%Y", models.DayOff.date) == str(year),
            func.strftime("%m", models.DayOff.date) == f"{month:02d}"
        )
        .order_by(models.DayOff.order)
        .all()
    )

    dayoffs = [
        {
            "employee_id": r.employee_id,
            "employee_order": r.employee_order,
            "name": r.name,
            "date": r.date.isoformat(),
            "order": r.order,
        }
        for r in results
    ]

    return dayoffs


def get_work_intersection(db: Session, year: int, month: int, names: List[str]):
    # 해당 연월의 전체 날짜
    num_days = calendar.monthrange(year, month)[1]
    workdays = {date(year, month, day) for day in range(1, num_days + 1)}

    # 이름 리스트에 유루디아 추가
    names.append("유루디아")

    # list 의 사람들의 휴일 조회
    dayoffs = (
        db.query(models.Employee.name, models.DayOff.date)
        .join(models.DayOff, models.Employee.id == models.DayOff.employee_id)  # type:ignore
        .filter(models.Employee.name.in_(names))
        .filter(
            func.strftime("%Y", models.DayOff.date) == str(year),
            func.strftime("%m", models.DayOff.date) == f"{month:02d}")
        .all()
    )

    # 직원들별 set 생성
    dayoff_map = defaultdict(set)
    for name, off_date in dayoffs:
        dayoff_map[name].add(off_date)

    # 전체 날짜에서 직원들의 근무일 제외
    for n in names:
        workdays -= dayoff_map.get(n, set())

    return {"dates": [d.isoformat() for d in sorted(workdays)]}


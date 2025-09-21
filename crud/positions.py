import models
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from schemas import Positions
from datetime import date


def get_employee_positions_by_month(db: Session, year: int, month: int, employee_id: int):
    positions = db.query(models.SpecialPosition).filter(
        models.SpecialPosition.employee_id == employee_id,
        func.strftime("%Y", models.SpecialPosition.date) == str(year),
        func.strftime("%m", models.SpecialPosition.date) == f"{month:02d}"
    ).order_by(models.SpecialPosition.date).all()

    data = [
        {
            "date": p.date.isoformat(),
            "position": p.position
        }
        for p in positions
    ]

    return {
        "employee_id": employee_id,
        "year": year,
        "month": month,
        "positions": data
    }


def upsert_employee_month_positions(db: Session, employee_id: int, year: int, month: int, positions: List[Positions]):
    # 기존 데이터 조회
    existing = db.query(models.SpecialPosition).filter(
        models.SpecialPosition.employee_id == employee_id,
        func.strftime("%Y", models.SpecialPosition.date) == str(year),
        func.strftime("%m", models.SpecialPosition.date) == f"{month:02d}"
    ).all()

    existing_map = {d.date.isoformat(): d for d in existing}
    position_map = {p.date: p.position for p in positions}

    # 기존에 있었는데 새로운 입력에는 없는 경우 삭제
    for day_date, positions_obj in existing_map.items():
        if day_date not in position_map:
            db.delete(positions_obj)

    # 새로 들어온 날짜들 순회
    for day_date in sorted(position_map.keys()):
        if day_date in existing_map:
            # update
            existing_map[day_date].position = position_map[day_date]
        else:
            # create
            new_position = models.SpecialPosition(
                employee_id=employee_id,
                date=date.fromisoformat(day_date),
                position=position_map[day_date]
            )
            db.add(new_position)

    db.commit()


def get_positions_by_month(db: Session, year: int, month: int):
    results = (
        db.query(
            models.SpecialPosition.employee_id,
            models.Employee.name,
            models.Employee.order.label("employee_order"),
            models.SpecialPosition.date,
            models.SpecialPosition.position,
        )
        .join(models.Employee, models.Employee.id == models.SpecialPosition.employee_id)  # type: ignore
        .filter(
            func.strftime("%Y", models.SpecialPosition.date) == str(year),
            func.strftime("%m", models.SpecialPosition.date) == f"{month:02d}"
        )
        .order_by(models.SpecialPosition.date)
        .all()
    )

    positions = [
        {
            "employee_id": r.employee_id,
            "employee_order": r.employee_order,
            "name": r.name,
            "positions": [
                {
                    "date": r.date.isoformat(),
                    "position": r.position
                }
            ]
        }
        for r in results
    ]

    return positions

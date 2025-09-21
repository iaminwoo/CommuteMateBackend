from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
import models
import schemas


def create_employee(db: Session, employee: schemas.EmployeeCreateAndUpdate):
    max_order = db.query(func.max(models.Employee.order)).scalar() or -1

    db_employee = models.Employee(**employee.dict())
    db_employee.order = max_order + 1
    db.add(db_employee)
    db.commit()


def get_employees(db: Session):
    return db.query(models.Employee).order_by(models.Employee.order).all()


def get_names(db: Session):
    employees = db.query(models.Employee.id, models.Employee.name).order_by(models.Employee.order).all()
    return [{"id": e.id, "name": e.name} for e in employees]


def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()


def update_employee(db: Session, employee_id: int, employee_update: schemas.EmployeeCreateAndUpdate):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        return None

    for key, value in employee_update.dict().items():
        setattr(db_employee, key, value)

    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employee_schedules(db: Session, date_str: str):
    employees = get_employees(db)

    query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    dayoffs = db.query(models.DayOff).filter(models.DayOff.date == query_date).all()

    # 휴무인 사람들의 id
    dayoff_ids = [d.employee_id for d in dayoffs]

    # 휴무가 아닌 사람들의 이름
    names = [e.name for e in employees if e.id not in dayoff_ids]

    # 파트별 분리
    parts = ["샌드위치", "오븐", "반죽", "빵", "시야기", "케이크"]
    part_dicts = {p: [] for p in parts}

    special_positions = db.query(models.SpecialPosition).filter(models.SpecialPosition.date == query_date).all()

    sp_dict = {sp.employee_id: sp.position for sp in special_positions}

    for e in employees:
        part_name = sp_dict.get(e.id, e.default_position)
        part_dicts[part_name].append(e.name)

    employee_part = [{"part_name": p, "employees": part_dicts[p]} for p in parts]

    # 파트너
    partner_obj = (db.query(models.SpecialPosition)
                   .filter(models.SpecialPosition.date == query_date)
                   .filter(models.SpecialPosition.position == "시야기")
                   .first())

    partner = "김지윤"  # 기본값
    if partner_obj:
        match = next((n.name for n in employees if n.id == partner_obj.employee_id), None)
        if match:
            partner = match

    # 남은 휴일
    yurudia = db.query(models.Employee).filter(models.Employee.name == "유루디아").first()

    if yurudia:
        next_dayoff = (
            db.query(models.DayOff)
            .filter(models.DayOff.employee_id == yurudia.id)  # type:ignore
            .filter(models.DayOff.date > query_date)
            .order_by(models.DayOff.date.asc())
            .first()
        )

        if next_dayoff:
            days_left = (next_dayoff.date - query_date).days
            days_left_str = f"{days_left}일 남음"

            if "유루디아" not in names:
                days_left_str = "휴일"
        else:
            days_left_str = "남은 휴일이 없습니다."

    else:
        days_left_str = "유루디아 정보를 찾을 수 없습니다."

    return {
        "date": date_str,
        "total": len(names),
        "employee_part": employee_part,
        "partner": partner,
        "next_dayoff": days_left_str
    }


def change_employee_order(db: Session, new_order: schemas.EmployeeOrderRequest):
    employees = db.query(models.Employee).all()
    employee_names = {e.name for e in employees}
    new_order_names = {name for name in new_order.order}

    if employee_names != new_order_names:
        missing = employee_names - new_order_names
        extra = new_order_names - employee_names
        raise HTTPException(status_code=400, detail=f"누락={missing}, 추가={extra}")

    new_order_dict = {
        name: idx
        for idx, name in enumerate(new_order.order)
    }

    for e in employees:
        e.order = new_order_dict[e.name]

    db.commit()

    return get_employee_response(employees)


def get_employee_response(employees):
    return {
        "new_order": [
            {"order": e.order or 0, "name": e.name}
            for e in sorted(employees, key=lambda x: x.order if x.order is not None else 0)
        ]
    }


def get_employee_order(db: Session):
    employees = db.query(models.Employee).all()
    return get_employee_response(employees)

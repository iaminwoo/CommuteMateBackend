from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(prefix="/dayoffs", tags=["dayoffs"])


# 한 직원의 한달 휴무 조회
@router.get("/dayoff-month/{employee_id}/{year}/{month}", response_model=schemas.DayOffEmployeeMonthResponse)
def get_employee_month_dayoffs(
    employee_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    return crud.get_employee_dayoffs_by_month(db, year, month, employee_id)


# 한 직원의 한달 휴무 수정
@router.post("/dayoff-month/")
def upsert_employee_month(dayoffs: schemas.EmployeeMonthDayOff, db: Session = Depends(get_db)):
    crud.upsert_employee_month_dayoffs(
        db,
        employee_id=dayoffs.employee_id,
        dates=dayoffs.dates,
        year=dayoffs.year,
        month=dayoffs.month
    )
    return {"message": "해당 직원의 한 달 휴무가 업데이트되었습니다."}


# 전체 직원의 한달 휴무 조회
@router.post("/month", response_model=schemas.DayOffMonthResponse)
def read_month_dayoffs(req: schemas.MonthDayOffRequest, db: Session = Depends(get_db)):
    dayoffs = crud.get_dayoffs_by_month(db, req.year, req.month)
    return {"dayoffs": dayoffs}


# 특정 직원들과 근무 교집합 조회
@router.post("/work-intersection")
def get_work_intersection(req: schemas.EmployeeWorkIntersectionRequest, db: Session = Depends(get_db)):
    return crud.get_work_intersection(db, req.year, req.month, req.names)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(prefix="/positions", tags=["positions"])


# 특정 직원의 한달 포지션 조회
@router.get("/position-month/{employee_id}/{year}/{month}", response_model=schemas.PositionsEmployeeMonth)
def get_employee_month_positions(
    employee_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    return crud.get_employee_positions_by_month(db, year, month, employee_id)


# 특정 직원의 한달 포지션 수정
@router.post("/position-month/")
def upsert_employee_month(positions: schemas.PositionsEmployeeMonth, db: Session = Depends(get_db)):
    crud.upsert_employee_month_positions(
        db,
        employee_id=positions.employee_id,
        year=positions.year,
        month=positions.month,
        positions=positions.positions
    )
    return {"message": "해당 직원의 한 달 포지션이 업데이트되었습니다."}


# 전체 직원의 한달 포지션 조회
@router.post("/month", response_model=schemas.PositionsEmployeeMonthResponse)
def read_month_positions(req: schemas.MonthDayOffRequest, db: Session = Depends(get_db)):
    positions = crud.get_positions_by_month(db, req.year, req.month)
    return {"positions": positions}

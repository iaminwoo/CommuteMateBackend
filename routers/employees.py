from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse
import schemas
import crud
from database import get_db

router = APIRouter(prefix="/employees", tags=["employees"])


# 직원 추가
@router.post("/")
def create(employee: schemas.EmployeeCreateAndUpdate, db: Session = Depends(get_db)):
    crud.create_employee(db, employee)
    return JSONResponse(
        content={"message": "직원이 성공적으로 추가되었습니다."},
        status_code=status.HTTP_201_CREATED
    )


# 직원 전체 조회
@router.get("/", response_model=schemas.EmployeeResponse)
def read_all(db: Session = Depends(get_db)):
    employees = crud.get_employees(db)
    return {"employees": employees}


# 직원 전체 이름 조회
@router.get("/names", response_model=schemas.EmployeeNamesResponse)
def get_names(db: Session = Depends(get_db)):
    employees_names = crud.get_names(db)
    return {"employees_names": employees_names}


# 직원 전체 순서 수정
@router.put("/order", response_model=schemas.EmployeeOrderResponse)
def change_employee_order(employee_order: schemas.EmployeeOrderRequest, db: Session = Depends(get_db)):
    return crud.change_employee_order(db, employee_order)


# 직원 전체 순서 조회
@router.get("/order", response_model=schemas.EmployeeOrderResponse)
def get_employee_order(db: Session = Depends(get_db)):
    return crud.get_employee_order(db)


# 특정 직원 조회
@router.get("/{employee_id}", response_model=schemas.EmployeeGetResponse)
def get_employee_detail(employee_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, employee_id)
    return {"employee": employee}


# 특정 직원 수정
@router.put("/{employee_id}", response_model=schemas.EmployeeGetResponse)
def update(employee_id: int, employee_update: schemas.EmployeeCreateAndUpdate, db: Session = Depends(get_db)):
    updated_employee = crud.update_employee(db, employee_id, employee_update)
    if not updated_employee:
        return JSONResponse(
            content={"message": "직원을 찾을 수 없습니다."},
            status_code=404
        )
    return {"employee": updated_employee}


# 특정 날의 근무 인원 조회
@router.get("/schedules/{date}", response_model=schemas.EmployeeSchedulesResponse)
def get_employee_schedules(date: str, db: Session = Depends(get_db)):
    return crud.get_employee_schedules(db, date)

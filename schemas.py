from typing import Optional, List
from pydantic import BaseModel
from datetime import date


class EmployeeBase(BaseModel):
    name: str
    default_position: Optional[str] = None


class EmployeeCreateAndUpdate(EmployeeBase):
    pass


class EmployeeGet(EmployeeBase):
    id: int

    class Config:
        from_attributes = True


class EmployeeGetResponse(BaseModel):
    employee: EmployeeGet


class EmployeeResponse(BaseModel):
    employees: List[EmployeeGet]


class EmployeeNamesGet(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class EmployeeNamesResponse(BaseModel):
    employees_names: List[EmployeeNamesGet]


class EmployeeMonthDayOff(BaseModel):
    employee_id: int
    year: int
    month: int
    dates: List[date]


class MonthDayOffRequest(BaseModel):
    year: int
    month: int


class DayOff(BaseModel):
    employee_id: int
    employee_order: int
    name: str
    date: str
    order: int


class DayOffMonthResponse(BaseModel):
    dayoffs: List[DayOff]


class DayOffEmployeeMonthResponse(BaseModel):
    employee_id: int
    year: int
    month: int
    dates: List[str]


class Positions(BaseModel):
    date: str
    position: str


class PositionsEmployeeMonth(BaseModel):
    employee_id: int
    year: int
    month: int
    positions: List[Positions]


class PositionsAllMonth(BaseModel):
    employee_id: int
    employee_order: int
    name: str
    positions: List[Positions]


class PositionsEmployeeMonthResponse(BaseModel):
    positions: List[PositionsAllMonth]


class Part(BaseModel):
    part_name: str
    employees: List[str]


class EmployeeSchedulesResponse(BaseModel):
    date: str
    total: int
    employee_part: List[Part]
    partner: str
    next_dayoff: str


class EmployeeOrderRequest(BaseModel):
    order: List[str]


class EmployeeOrder(BaseModel):
    order: int
    name: str


class EmployeeOrderResponse(BaseModel):
    new_order: List[EmployeeOrder]


class EmployeeWorkIntersectionRequest(BaseModel):
    year: int
    month: int
    names: List[str]
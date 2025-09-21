from sqlalchemy import Column, Integer, String, Date
from database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    default_position = Column(String, nullable=True)  # 기본 포지션
    order = Column(Integer, index=True)


class DayOff(Base):
    __tablename__ = "day_offs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    date = Column(Date)
    order = Column(Integer)  # 휴일 번호


class SpecialPosition(Base):
    __tablename__ = "special_positions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    date = Column(Date)
    position = Column(String)  # 근무 형태

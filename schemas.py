from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Client(BaseModel):
    id: Optional[int]
    name: str

    class Config:
        orm_mode = True


class Account(BaseModel):
    amount_available: float
    client_id: int

    class Config:
        orm_mode = True


class Amount(BaseModel):
    amount_available: float

    class Config:
        orm_mode = True


class Response(BaseModel):
    message: str


class CreateMovementDetail(BaseModel):
    amount: float
    type: str

    class Config:
        orm_mode = True


class Movement(BaseModel):
    id: Optional[int]
    date: datetime
    client_id: int
    details: List[CreateMovementDetail]

    class Config:
        orm_mode = True


class MovementDetail(BaseModel):
    movement: int
    amount: float
    type: str

    class Config:
        orm_mode = True

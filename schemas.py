from pydantic import BaseModel

class Client(BaseModel):
    id:int
    name:str

    class Config:
        orm_mode = True

class Account(BaseModel):
    amount_available:float

class Response(BaseModel):
    message:str
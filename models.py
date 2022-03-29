from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from db import Base

class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))


# class Account(Base):
#     __tablename__ = 'account'

#     client = relationship("Client", back_populates="account")
#     amount_available = Column(Float)
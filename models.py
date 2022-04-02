from sqlalchemy import Column, Float, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import validates, relationship, backref
from datetime import datetime
from db import Base
import requests
from sqlalchemy.ext.hybrid import hybrid_property


class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))


class Account(Base):
    __tablename__ = 'account'

    amount_available = Column(Float)
    client_id = Column(Integer, ForeignKey('client.id'), primary_key=True)

    def entry_amount(self, amount):
        self.amount_available = self.amount_available + amount

    def check_amount(self, amount):
        if self.amount_available - amount < 0:
            raise ValueError('El monto no puede ser negativo')
        else: return True

    def rest_amount(self, amount):
        self.amount_available = self.amount_available - amount

    @hybrid_property
    def get_total_usd(self):
        response = requests.get('https://www.dolarsi.com/api/api.php?type=valoresprincipales')
        if response.status_code == 200:
            value = response.json()[1]['casa']['compra']
            dolar_value = value.replace(",", ".")
            return self.get_total * float(dolar_value)
        return 0


class Movement(Base):
    __tablename__ = 'movement'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now)
    client_id = Column(Integer, ForeignKey('client.id'))


class MovementDetail(Base):
    __tablename__ = 'detail_movement'

    id = Column(Integer, primary_key=True, index=True)
    movement_id = Column(Integer, ForeignKey('movement.id', ondelete="CASCADE"))
    movement = relationship(Movement, backref=backref("details", cascade="all,delete"))
    amount = Column(Float)
    type = Column(String(10))

from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from typing import List

from pydantic import ValidationError
import models
import schemas
from starlette.responses import RedirectResponse
from db import SessionLocal, engine
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close


@app.get('/')
def main():
    return RedirectResponse(url="/docs/")


@app.get('/clients/', response_model=List[schemas.Client])
def list_clients(db: Session = Depends(get_db)):
    clients = db.query(models.Client).all()
    return clients


@app.post('/clients/', response_model=schemas.Client)
def create_client(data: schemas.Client, db: Session = Depends(get_db)):
    try:
        client = models.Client(name=data.name)
        db.add(client)
        db.commit()
        db.refresh(client)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return client


@app.put('/clients/{client_id}', response_model=schemas.Client)
def update_client(client_id: int, data: schemas.Client, db: Session = Depends(get_db)):
    try:
        client = db.query(models.Client).filter_by(id=client_id).first()
        client.name = data.name
        db.commit()
        db.refresh(client)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return client


@app.delete('/clients/{client_id}', response_model=schemas.Response)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter_by(id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="El cliente no existe")
    db.delete(client)
    db.commit()
    message = schemas.Response(message="El cliente fue eliminado exitosamente")
    return message


@app.get('/clients/{client_id}', response_model=schemas.Client)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter_by(id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="El cliente no existe")
    return client


@app.post('/accounts/', response_model=schemas.Account)
def create_account(data: schemas.Account, db: Session = Depends(get_db)):
    try:
        account = models.Account(
            client_id=data.client_id, amount_available=data.amount_available)
        db.add(account)
        db.commit()
        db.refresh(account)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return account


@app.get('/movements/{movement_id}', response_model=schemas.Movement)
def get_movement(movement_id: int, db: Session = Depends(get_db)):
    movement = db.query(
        models.Movement).filter_by(id=movement_id).first()
    if not movement:
        raise HTTPException(status_code=404, detail="El movimiento no existe")
    return movement


def get_total_egress(details):
    total = 0
    [total := total + detail.amount if detail.type ==
        "egreso" else total + 0 for detail in details]
    return total


def get_total_entry(details):
    total = 0
    [total := total + detail.amount if detail.type ==
        "ingreso" else total + 0 for detail in details]
    return total


@app.post('/movements/', response_model=schemas.Movement)
def create_movement(data: schemas.Movement, db:Session=Depends(get_db)):
    account = db.query(models.Account).filter_by(
        client_id=data.client_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="El cliente no posee cuenta")

    total_egress = get_total_egress(data.details)
    try:
        account.check_amount(total_egress)
        movement = models.Movement(date=data.date, client_id=data.client_id)
        total_entry = get_total_entry(data.details)
        for detail in data.details:
            movement_detail = models.MovementDetail(movement=movement, amount=detail.amount, type=detail.type)
            movement.details.append(movement_detail)
        
        account.entry_amount(total_entry)
        account.rest_amount(total_egress)

    except (ValidationError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.add(movement)
    db.commit()
    db.refresh(movement)
    db.refresh(account)
    return movement



@app.delete('/movements/{movement_id}', response_model=schemas.Response)
def delete_movement(movement_id: int, db:Session=Depends(get_db)):
    movement = db.query(models.Movement).filter_by(id=movement_id).first()

    if not movement:
        raise HTTPException(status_code=404, detail="El movimiento no existe")

    account = db.query(models.Account).filter_by(
        client_id=movement.client_id).first()

    total_egress = get_total_egress(movement.details)
    total_entry = get_total_entry(movement.details)
    account.check_amount(total_egress)

    account.entry_amount(total_egress)
    account.rest_amount(total_entry)

    db.refresh(account)
    db.delete(movement)
    db.commit()
    return schemas.Response(message="El movimiento fue eliminado exitosamente")


@app.get('/get-amount/{client_id}', response_model=schemas.Amount)
def get_amount_available(client_id: int, db:Session=Depends(get_db)):
    account = db.query(models.Account).filter_by(client_id=client_id).first()
    if not account:
        raise HTTPException(
            status_code=404, detail="El cliente o la cuenta no existen")
    return account

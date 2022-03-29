from fastapi import Depends, FastAPI
from typing import List
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
def get_clients(db:Session=Depends(get_db)):
    clients = db.query(models.Client).all()
    return clients


@app.post('/clients/', response_model=schemas.Client)
def create_client(data:schemas.Client, db:Session=Depends(get_db)):
    client = models.Client(name=data.name)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@app.put('/clients/{client_id}', response_model=schemas.Client)
def update_client(client_id:int, data:schemas.Client, db:Session=Depends(get_db)):
    client = db.query(models.Client).filter_by(id=client_id).first()
    client.name = data.name
    db.commit()
    db.refresh(client)
    return client


@app.delete('/clients/{client_id}', response_model=schemas.Response)
def delete_client(client_id:int, db:Session=Depends(get_db)):
    client = db.query(models.Client).filter_by(id=client_id).first()
    db.delete(client)
    db.commit()
    message = schemas.Response(message="El cliente fue eliminado exitosamente")
    return message
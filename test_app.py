from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base
from app import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_client():
    response = client.post("/clients/",
                           json={
                               "id": 1,
                               "name": "Deivid"
                           })
    assert response.status_code == 200
    assert "Deivid" in response.json().values()


def test_get_client():
    response = client.get("/clients/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Deivid"}


def test_list_clients():
    response = client.post("/clients/",
                           json={
                               "id": 2,
                               "name": "Nala"
                           })
    response = client.get("/clients/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_client():
    response = client.delete("/clients/1")
    assert response.status_code == 200


def test_create_movement_ok():
    response = client.post("/accounts/",
                           json={
                               "amount_available": 12,
                               "client_id": 2
                           })

    response = client.post("/movements/",
                           json={
                               "id": 1,
                               "date": "2022-04-01T01:23:20.189Z",
                               "client_id": 2,
                               "details": [
                                   {
                                       "amount": 12.4,
                                       "type": "ingreso"
                                   },
                                   {
                                       "amount": 2.7,
                                       "type": "egreso"
                                   }
                               ]
                           })
    assert response.status_code == 200
    assert response.json()['details'] == [{'amount': 12.4, 'type': 'ingreso'}, {
        'amount': 2.7, 'type': 'egreso'}]


def test_create_movement_with_error():
    response = client.post("/movements/",
                           json={
                               "date": "2022-04-01T01:23:20.189Z",
                               "client_id": 2,
                               "details": [
                                   {
                                       "amount": 1,
                                       "type": "ingreso"
                                   },
                                   {
                                       "amount": 180,
                                       "type": "egreso"
                                   }
                               ]
                           })
    assert response.json()['detail'] == "El monto no puede ser negativo"
    assert response.status_code == 400


def test_get_movement():
    response = client.get("/movements/1")
    assert response.status_code == 200
    assert response.json()['details'] == [
        {'amount': 12.4, 'type': 'ingreso'}, 
        {'amount': 2.7, 'type': 'egreso'}]


def test_get_amount_available():
    response = client.get("/get-amount/2")
    assert response.status_code == 200
    assert response.json() == {'amount_available': 21.7}


def test_delete_movement():
    response = client.delete("/movements/1")
    assert response.status_code == 200
    # chequear monto de la cuenta
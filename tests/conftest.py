import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base

# тестовая БД — отдельный файл чтобы не портить основную
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    # создаём таблицы перед тестом
    Base.metadata.create_all(bind=engine)
    yield
    # после теста всё удаляем
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    # подменяем зависимость БД на тестовую
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_token(client):
    # регистрируем тестового студента
    client.post(
        "/api/auth/register",
        json={
            "name": "Тестовый Студент",
            "email": "test@example.com",
            "password": "password123",
            "role": "student",
        },
    )
    # логинимся и получаем токен
    resp = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "password123"},
    )
    return resp.json()["access_token"]


@pytest.fixture
def employer_token(client):
    # регистрируем тестового работодателя
    client.post(
        "/api/auth/register",
        json={
            "name": "Тестовый Работодатель",
            "email": "employer@example.com",
            "password": "password123",
            "role": "employer",
        },
    )
    # логинимся
    resp = client.post(
        "/api/auth/login",
        data={"username": "employer@example.com", "password": "password123"},
    )
    return resp.json()["access_token"]

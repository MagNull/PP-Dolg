# тесты авторизации


def test_register_success(client):
    """регистрация с корректными данными"""
    resp = client.post(
        "/api/auth/register",
        json={
            "name": "Иван Иванов",
            "email": "ivan@example.com",
            "password": "mypassword",
            "role": "student",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "ivan@example.com"
    assert data["name"] == "Иван Иванов"


def test_register_duplicate_email(client):
    """проверяем что нельзя зарегистрироваться дважды с одним email"""
    user_data = {
        "name": "Петр Петров",
        "email": "petr@example.com",
        "password": "password123",
        "role": "student",
    }
    # первый раз — ок
    resp1 = client.post("/api/auth/register", json=user_data)
    assert resp1.status_code == 200

    # второй раз — ошибка
    resp2 = client.post("/api/auth/register", json=user_data)
    assert resp2.status_code == 400


def test_register_invalid_email(client):
    """некорректный email должен вернуть 422"""
    resp = client.post(
        "/api/auth/register",
        json={
            "name": "Кто-то",
            "email": "не-email",
            "password": "password123",
            "role": "student",
        },
    )
    assert resp.status_code == 422


def test_login_success(client):
    """успешный логин после регистрации"""
    # сначала регистрируемся
    client.post(
        "/api/auth/register",
        json={
            "name": "Анна Смирнова",
            "email": "anna@example.com",
            "password": "anna12345",
            "role": "student",
        },
    )

    # логинимся (username = email, так работает OAuth2)
    resp = client.post(
        "/api/auth/login",
        data={"username": "anna@example.com", "password": "anna12345"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """неверный пароль — 401"""
    # регистрируемся
    client.post(
        "/api/auth/register",
        json={
            "name": "Мария",
            "email": "maria@example.com",
            "password": "rightpassword",
            "role": "student",
        },
    )

    # пытаемся войти с неверным паролем
    resp = client.post(
        "/api/auth/login",
        data={"username": "maria@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_me_authorized(client, auth_token):
    """получаем профиль с токеном"""
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "student"


def test_me_unauthorized(client):
    """без токена — 401"""
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_employer_returns_company_name(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "ООО Кампус",
            "email": "hr@example.com",
            "password": "strongpass",
            "role": "employer",
            "company_name": "Кампус Лабс",
        },
    )

    login_resp = client.post(
        "/api/auth/login",
        data={"username": "hr@example.com", "password": "strongpass"},
    )
    token = login_resp.json()["access_token"]

    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "employer"
    assert data["company_name"] == "Кампус Лабс"

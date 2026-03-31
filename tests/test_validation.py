# тесты валидации данных


def test_register_short_password(client):
    """пароль меньше 6 символов — ошибка валидации"""
    resp = client.post(
        "/api/auth/register",
        json={"email": "a@b.com", "password": "123", "name": "Тест", "role": "student"},
    )
    assert resp.status_code == 422
    data = resp.json()
    assert "errors" in data
    # проверяем что есть ошибка по полю password
    fields = [e["поле"] for e in data["errors"]]
    assert "password" in fields


def test_register_short_name(client):
    """имя меньше 2 символов"""
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "a@b.com",
            "password": "password123",
            "name": "А",
            "role": "student",
        },
    )
    assert resp.status_code == 422


def test_register_invalid_role(client):
    """недопустимая роль — ошибка"""
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "a@b.com",
            "password": "password123",
            "name": "Тест",
            "role": "admin",
        },
    )
    assert resp.status_code == 422
    data = resp.json()
    fields = [e["поле"] for e in data["errors"]]
    assert "role" in fields


def test_register_missing_fields(client):
    """без обязательных полей"""
    resp = client.post("/api/auth/register", json={})
    assert resp.status_code == 422
    data = resp.json()
    assert len(data["errors"]) >= 3  # email, password, name


def test_vacancy_invalid_employment_type(client, employer_token):
    """неверный тип занятости"""
    from tests.conftest import TestSessionLocal
    from app.models import Category

    db = TestSessionLocal()
    cat = Category(name="Тест")
    db.add(cat)
    db.flush()
    cat_id = cat.id
    db.commit()
    db.close()

    headers = {"Authorization": f"Bearer {employer_token}"}
    resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Вакансия",
            "description": "Описание вакансии достаточной длины",
            "employment_type": "invalid_type",
            "category_id": cat_id,
        },
        headers=headers,
    )
    assert resp.status_code == 422
    data = resp.json()
    fields = [e["поле"] for e in data["errors"]]
    assert "employment_type" in fields


def test_vacancy_short_title(client, employer_token):
    """слишком короткое название вакансии"""
    headers = {"Authorization": f"Bearer {employer_token}"}
    resp = client.post(
        "/api/vacancies/",
        json={
            "title": "AB",
            "description": "Описание вакансии достаточной длины",
            "employment_type": "internship",
            "category_id": 1,
        },
        headers=headers,
    )
    assert resp.status_code == 422


def test_vacancy_salary_range_invalid(client, employer_token):
    """salary_to < salary_from — ошибка"""
    from tests.conftest import TestSessionLocal
    from app.models import Category, Employer, User

    db = TestSessionLocal()
    existing = db.query(Category).first()
    if not existing:
        cat = Category(name="IT2")
        db.add(cat)
        db.flush()
        cat_id = cat.id
    else:
        cat_id = existing.id

    user = db.query(User).filter(User.email == "employer@example.com").first()
    if user and not user.employer:
        db.add(Employer(user_id=user.id, company_name="Компания"))
    db.commit()
    db.close()

    headers = {"Authorization": f"Bearer {employer_token}"}
    resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Тестовая вакансия",
            "description": "Описание вакансии достаточной длины",
            "employment_type": "part_time",
            "category_id": cat_id,
            "salary_from": 50000,
            "salary_to": 10000,
        },
        headers=headers,
    )
    assert resp.status_code == 422


def test_application_empty_cover_letter_valid(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client.post(
        "/api/applications/",
        json={"vacancy_id": 1, "cover_letter": ""},
        headers=headers,
    )
    assert resp.status_code != 422


def test_review_rating_out_of_range(client, auth_token):
    """рейтинг вне диапазона 1-5"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client.post(
        "/api/reviews",
        json={"vacancy_id": 1, "rating": 10, "text": "Отличная вакансия"},
        headers=headers,
    )
    assert resp.status_code == 422
    data = resp.json()
    fields = [e["поле"] for e in data["errors"]]
    assert "rating" in fields


def test_review_short_text(client, auth_token):
    """текст отзыва меньше 5 символов"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client.post(
        "/api/reviews",
        json={"vacancy_id": 1, "rating": 3, "text": "Ок"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_validation_error_format(client):
    """проверяем формат ответа при ошибке валидации"""
    resp = client.post("/api/auth/register", json={"email": "bad", "password": "1"})
    assert resp.status_code == 422
    data = resp.json()
    # наш кастомный формат
    assert data["detail"] == "Введите корректный email"
    assert "errors" in data
    assert isinstance(data["errors"], list)
    # каждая ошибка имеет нужные поля
    for err in data["errors"]:
        assert "поле" in err
        assert "сообщение" in err
        assert "тип_ошибки" in err

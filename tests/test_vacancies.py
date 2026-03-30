# тесты для вакансий

from tests.conftest import TestSessionLocal
from app.models import Category, Employer, User


def _подготовить_данные():
    """добавляем категорию и профиль работодателя в тестовую БД"""
    db = TestSessionLocal()

    # категория нужна для создания вакансии
    cat = Category(name="IT")
    db.add(cat)
    db.flush()
    cat_id = cat.id

    # создаём профиль работодателя (без него нельзя постить вакансии)
    user = db.query(User).filter(User.email == "employer@example.com").first()
    if user:
        emp = Employer(user_id=user.id, company_name="Тест Компания")
        db.add(emp)

    db.commit()
    db.close()
    return cat_id


def test_get_vacancies_empty(client):
    """список вакансий — пустой если ничего не создавали"""
    resp = client.get("/api/vacancies/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_vacancy_employer(client, employer_token):
    """работодатель создаёт вакансию"""
    cat_id = _подготовить_данные()

    headers = {"Authorization": f"Bearer {employer_token}"}
    resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Python разработчик",
            "description": "Ищем джуна на подработку в офис",
            "employment_type": "part_time",
            "category_id": cat_id,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Python разработчик"
    assert data["employment_type"] == "part_time"


def test_get_vacancy_detail(client, employer_token):
    """получаем вакансию по id"""
    cat_id = _подготовить_данные()

    # создаём вакансию
    headers = {"Authorization": f"Bearer {employer_token}"}
    create_resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Стажёр аналитик",
            "description": "Стажировка в отделе аналитики данных",
            "employment_type": "internship",
            "category_id": cat_id,
        },
        headers=headers,
    )
    vacancy_id = create_resp.json()["id"]

    # запрашиваем деталь
    resp = client.get(f"/api/vacancies/{vacancy_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Стажёр аналитик"


def test_get_vacancy_not_found(client):
    """несуществующая вакансия — 404"""
    resp = client.get("/api/vacancies/99999")
    assert resp.status_code == 404


def test_filter_vacancies_by_category(client, employer_token):
    """фильтрация по категории"""
    cat_id = _подготовить_данные()

    headers = {"Authorization": f"Bearer {employer_token}"}
    # создаём вакансию в категории
    client.post(
        "/api/vacancies/",
        json={
            "title": "Тестировщик ПО",
            "description": "Ручное тестирование веб-приложений",
            "employment_type": "full_time",
            "category_id": cat_id,
        },
        headers=headers,
    )

    # фильтруем по этой категории
    resp = client.get(f"/api/vacancies/?category_id={cat_id}")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # по несуществующей категории — пусто
    resp2 = client.get("/api/vacancies/?category_id=999")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 0


def test_create_vacancy_student_forbidden(client, auth_token):
    """студент не может создавать вакансии — 403"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Не получится",
            "description": "Студентам нельзя создавать вакансии",
            "employment_type": "full_time",
            "category_id": 1,
        },
        headers=headers,
    )
    assert resp.status_code == 403

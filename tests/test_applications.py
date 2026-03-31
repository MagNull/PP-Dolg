# тесты для заявок на вакансии

from tests.conftest import TestSessionLocal
from app.models import Category, ApplicationStatus


def _подготовить_данные():
    """добавляем справочники"""
    db = TestSessionLocal()

    cat = Category(name="IT")
    db.add(cat)

    app_status = ApplicationStatus(name="На рассмотрении")
    db.add(app_status)

    db.flush()
    cat_id = cat.id

    db.commit()
    db.close()
    return cat_id


def _создать_вакансию(client, employer_token, cat_id):
    """создаём вакансию от работодателя — нужна для подачи заявки"""
    headers = {"Authorization": f"Bearer {employer_token}"}
    resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Помощник в офис",
            "description": "Нужен студент для работы в офисе",
            "employment_type": "part_time",
            "category_id": cat_id,
        },
        headers=headers,
    )
    return resp.json()["id"]


def test_apply_success(client, auth_token, employer_token):
    """студент подаёт заявку на вакансию"""
    cat_id = _подготовить_данные()
    vacancy_id = _создать_вакансию(client, employer_token, cat_id)

    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client.post(
        "/api/applications/",
        json={
            "vacancy_id": vacancy_id,
            "cover_letter": "Хочу работать, есть свободное время",
        },
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["vacancy_id"] == vacancy_id
    assert data["status_name"] == "На рассмотрении"


def test_apply_duplicate(client, auth_token, employer_token):
    """повторная заявка на ту же вакансию — ошибка"""
    cat_id = _подготовить_данные()
    vacancy_id = _создать_вакансию(client, employer_token, cat_id)

    headers = {"Authorization": f"Bearer {auth_token}"}
    # первый раз — ок
    client.post(
        "/api/applications/",
        json={
            "vacancy_id": vacancy_id,
            "cover_letter": "Подаю заявку первый раз",
        },
        headers=headers,
    )

    # второй раз — 400
    resp = client.post(
        "/api/applications/",
        json={
            "vacancy_id": vacancy_id,
            "cover_letter": "Пытаюсь подать ещё раз",
        },
        headers=headers,
    )
    assert resp.status_code == 400


def test_my_applications(client, auth_token, employer_token):
    """получаем список своих заявок"""
    cat_id = _подготовить_данные()
    vacancy_id = _создать_вакансию(client, employer_token, cat_id)

    headers = {"Authorization": f"Bearer {auth_token}"}
    # подаём заявку
    client.post(
        "/api/applications/",
        json={
            "vacancy_id": vacancy_id,
            "cover_letter": "Заявка для проверки списка",
        },
        headers=headers,
    )

    # проверяем что заявка есть в списке
    resp = client.get("/api/applications/my", headers=headers)
    assert resp.status_code == 200
    apps = resp.json()
    assert len(apps) >= 1
    assert apps[0]["vacancy_id"] == vacancy_id


def test_apply_employer_forbidden(client, employer_token):
    """работодатель не может подавать заявки — 403"""
    cat_id = _подготовить_данные()
    vacancy_id = _создать_вакансию(client, employer_token, cat_id)

    headers = {"Authorization": f"Bearer {employer_token}"}
    resp = client.post(
        "/api/applications/",
        json={
            "vacancy_id": vacancy_id,
            "cover_letter": "Работодатель не должен подавать заявки",
        },
        headers=headers,
    )
    assert resp.status_code == 403


def test_delete_application(client, auth_token, employer_token):
    """удаление своей заявки"""
    cat_id = _подготовить_данные()
    vacancy_id = _создать_вакансию(client, employer_token, cat_id)

    headers = {"Authorization": f"Bearer {auth_token}"}
    # подаём
    resp = client.post(
        "/api/applications/",
        json={
            "vacancy_id": vacancy_id,
            "cover_letter": "Заявка которую потом удалим",
        },
        headers=headers,
    )
    app_id = resp.json()["id"]

    # удаляем
    del_resp = client.delete(f"/api/applications/{app_id}", headers=headers)
    assert del_resp.status_code == 200

    # проверяем что заявок больше нет
    my_resp = client.get("/api/applications/my", headers=headers)
    assert len(my_resp.json()) == 0

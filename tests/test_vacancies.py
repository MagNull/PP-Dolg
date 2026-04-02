# тесты для вакансий

from pathlib import Path

from jose import jwt

from tests.conftest import TestSessionLocal
from app.models import Category, ApplicationStatus, Application, Skill
from app.routes.auth import SECRET_KEY, ALGORITHM


def _подготовить_данные():
    """добавляем категорию в тестовую БД"""
    db = TestSessionLocal()

    cat = Category(name="IT")
    db.add(cat)
    db.flush()
    cat_id = cat.id

    db.commit()
    db.close()
    return cat_id


def test_get_vacancies_empty(client):
    """список вакансий — пустой если ничего не создавали"""
    resp = client.get("/api/vacancies/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


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
    assert len(resp.json()["items"]) >= 1

    # по несуществующей категории — пусто
    resp2 = client.get("/api/vacancies/?category_id=999")
    assert resp2.status_code == 200
    assert len(resp2.json()["items"]) == 0


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


def test_delete_vacancy_with_applications(client, auth_token, employer_token):
    db = TestSessionLocal()
    cat = Category(name="IT")
    status_obj = ApplicationStatus(name="На рассмотрении")
    db.add(cat)
    db.add(status_obj)
    db.commit()
    cat_id = cat.id
    db.close()

    employer_headers = {"Authorization": f"Bearer {employer_token}"}
    create_resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Python разработчик",
            "description": "Ищем джуна на подработку в офис",
            "employment_type": "part_time",
            "category_id": cat_id,
        },
        headers=employer_headers,
    )
    vacancy_id = create_resp.json()["id"]

    student_headers = {"Authorization": f"Bearer {auth_token}"}
    apply_resp = client.post(
        "/api/applications/",
        json={"vacancy_id": vacancy_id, "cover_letter": None},
        headers=student_headers,
    )
    assert apply_resp.status_code == 200

    delete_resp = client.delete(
        f"/api/vacancies/{vacancy_id}", headers=employer_headers
    )
    assert delete_resp.status_code == 204

    check_resp = client.get(f"/api/vacancies/{vacancy_id}")
    assert check_resp.status_code == 404


def test_vacancies_list_returns_my_application_status(
    client, auth_token, employer_token
):
    db = TestSessionLocal()
    cat = Category(name="IT")
    db.add(cat)
    db.add(ApplicationStatus(id=1, name="На рассмотрении"))
    db.add(ApplicationStatus(id=3, name="Принято"))
    db.commit()
    cat_id = cat.id
    db.close()

    employer_headers = {"Authorization": f"Bearer {employer_token}"}
    create_resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Python разработчик",
            "description": "Ищем джуна на подработку в офис",
            "employment_type": "part_time",
            "category_id": cat_id,
        },
        headers=employer_headers,
    )
    vacancy_id = create_resp.json()["id"]

    student_headers = {"Authorization": f"Bearer {auth_token}"}
    apply_resp = client.post(
        "/api/applications/",
        json={"vacancy_id": vacancy_id, "cover_letter": None},
        headers=student_headers,
    )
    assert apply_resp.status_code == 200

    db = TestSessionLocal()
    app = db.query(Application).filter(Application.vacancy_id == vacancy_id).first()
    app.status_id = 3
    db.commit()
    db.close()

    resp = client.get("/api/vacancies/", headers=student_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    vacancy = next(v for v in items if v["id"] == vacancy_id)
    assert vacancy["my_status_id"] == 3
    assert vacancy["my_status_name"] == "Принято"


def test_vacancy_detail_returns_my_application_status(
    client, auth_token, employer_token
):
    db = TestSessionLocal()
    cat = Category(name="IT")
    db.add(cat)
    db.add(ApplicationStatus(id=1, name="На рассмотрении"))
    db.add(ApplicationStatus(id=4, name="Отклонено"))
    db.commit()
    cat_id = cat.id
    db.close()

    employer_headers = {"Authorization": f"Bearer {employer_token}"}
    create_resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Аналитик",
            "description": "Ищем студента на помощь в аналитике",
            "employment_type": "internship",
            "category_id": cat_id,
        },
        headers=employer_headers,
    )
    vacancy_id = create_resp.json()["id"]

    student_headers = {"Authorization": f"Bearer {auth_token}"}
    apply_resp = client.post(
        "/api/applications/",
        json={"vacancy_id": vacancy_id, "cover_letter": None},
        headers=student_headers,
    )
    assert apply_resp.status_code == 200

    db = TestSessionLocal()
    app = db.query(Application).filter(Application.vacancy_id == vacancy_id).first()
    app.status_id = 4
    db.commit()
    db.close()

    resp = client.get(f"/api/vacancies/{vacancy_id}", headers=student_headers)
    assert resp.status_code == 200
    vacancy = resp.json()
    assert vacancy["my_status_id"] == 4
    assert vacancy["my_status_name"] == "Отклонено"


def test_public_vacancies_ignore_bad_token(client, employer_token):
    cat_id = _подготовить_данные()

    headers = {"Authorization": f"Bearer {employer_token}"}
    create_resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Оператор ПК",
            "description": "Нужен студент для помощи с документами в офисе",
            "employment_type": "part_time",
            "category_id": cat_id,
        },
        headers=headers,
    )
    vacancy_id = create_resp.json()["id"]

    bad_token = jwt.encode({"sub": "abc"}, SECRET_KEY, algorithm=ALGORITHM)
    public_headers = {"Authorization": f"Bearer {bad_token}"}

    list_resp = client.get("/api/vacancies/", headers=public_headers)
    assert list_resp.status_code == 200
    vacancy = next(v for v in list_resp.json()["items"] if v["id"] == vacancy_id)
    assert vacancy["my_status_id"] is None
    assert vacancy["my_status_name"] is None

    detail_resp = client.get(f"/api/vacancies/{vacancy_id}", headers=public_headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["my_status_id"] is None
    assert detail["my_status_name"] is None


def test_vacancy_page_message_does_not_repeat_status_text():
    page = Path("static/vacancy.html").read_text(encoding="utf-8")
    assert ". Статус: <strong>" not in page


def test_create_vacancy_saves_selected_skills(client, employer_token):
    db = TestSessionLocal()
    cat = Category(name="IT")
    skill1 = Skill(name="Python")
    skill2 = Skill(name="SQL")
    db.add(cat)
    db.add(skill1)
    db.add(skill2)
    db.commit()
    cat_id = cat.id
    skill_ids = [skill1.id, skill2.id]
    db.close()

    headers = {"Authorization": f"Bearer {employer_token}"}
    resp = client.post(
        "/api/vacancies/",
        json={
            "title": "Python разработчик",
            "description": "Нужен студент со знанием Python и SQL для проекта",
            "employment_type": "part_time",
            "category_id": cat_id,
            "skill_ids": skill_ids,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert sorted(data["skills"]) == ["Python", "SQL"]


def test_profile_page_has_skill_field_for_vacancy_form():
    page = Path("static/profile.html").read_text(encoding="utf-8")
    assert 'id="vacSkillsInput"' in page


def test_profile_page_has_collapsible_vacancy_form_controls():
    page = Path("static/profile.html").read_text(encoding="utf-8")
    assert 'id="toggleVacancyFormBtn"' in page
    assert 'id="createVacancyForm"' in page
    assert "Свернуть форму" in page


def test_profile_page_scrolls_to_form_and_updates_toggle_state():
    page = Path("static/profile.html").read_text(encoding="utf-8")
    assert "scrollIntoView" in page
    assert "toggleVacancyFormBtn" in page
    assert "btn-outline-secondary" in page
    assert "btn-success" in page

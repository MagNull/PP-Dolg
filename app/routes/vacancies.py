from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Vacancy, User
from app.schemas import VacancyCreate, VacancyResponse, VacancyListResponse
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/vacancies", tags=["vacancies"])


# собираем ответ из модели вакансии
def vacancy_to_response(v: Vacancy) -> VacancyResponse:
    return VacancyResponse(
        id=v.id,
        title=v.title,
        description=v.description,
        employment_type=v.employment_type,
        salary_from=v.salary_from,
        salary_to=v.salary_to,
        is_active=v.is_active,
        created_at=v.created_at,
        employer_name=v.employer.company_name if v.employer else None,
        category_name=v.category.name if v.category else None,
        skills=[s.skill.name for s in v.skills] if v.skills else [],
    )


# получаем список вакансий с фильтрами
@router.get("/", response_model=VacancyListResponse)
def get_vacancies(
    category_id: Optional[int] = None,
    employment_type: Optional[str] = None,
    employer_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Vacancy)

    # фильтры
    if category_id:
        query = query.filter(Vacancy.category_id == category_id)
    if employment_type:
        query = query.filter(Vacancy.employment_type == employment_type)
    if employer_id:
        query = query.filter(Vacancy.employer_id == employer_id)
    if search:
        query = query.filter(Vacancy.title.ilike(f"%{search}%"))

    total = query.count()
    vacancies = query.offset(skip).limit(limit).all()
    return VacancyListResponse(
        items=[vacancy_to_response(v) for v in vacancies], total=total
    )


# получаем вакансию по id
@router.get("/{vacancy_id}", response_model=VacancyResponse)
def get_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    return vacancy_to_response(vacancy)


# создаём вакансию (только для работодателей)
@router.post("/", response_model=VacancyResponse, status_code=status.HTTP_201_CREATED)
def create_vacancy(
    data: VacancyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # проверяем что пользователь — работодатель
    if current_user.role != "employer":
        raise HTTPException(
            status_code=403, detail="Только работодатели могут создавать вакансии"
        )

    if not current_user.employer:
        raise HTTPException(status_code=400, detail="Профиль работодателя не найден")

    # создаём вакансию, employer_id берём из текущего пользователя
    vacancy = Vacancy(
        employer_id=current_user.employer.id,
        category_id=data.category_id,
        title=data.title,
        description=data.description,
        employment_type=data.employment_type,
        salary_from=data.salary_from,
        salary_to=data.salary_to,
    )
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)

    return vacancy_to_response(vacancy)


# обновляем вакансию
@router.put("/{vacancy_id}", response_model=VacancyResponse)
def update_vacancy(
    vacancy_id: int,
    data: VacancyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")

    # проверяем права — только владелец может редактировать
    if not current_user.employer or vacancy.employer_id != current_user.employer.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой вакансии")

    # обновляем поля
    vacancy.title = data.title
    vacancy.description = data.description
    vacancy.category_id = data.category_id
    vacancy.employment_type = data.employment_type
    vacancy.salary_from = data.salary_from
    vacancy.salary_to = data.salary_to

    db.commit()
    db.refresh(vacancy)

    return vacancy_to_response(vacancy)


# удаляем вакансию
@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vacancy(
    vacancy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")

    # проверяем права
    if not current_user.employer or vacancy.employer_id != current_user.employer.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой вакансии")

    db.delete(vacancy)
    db.commit()

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import MIN_STATUS_ID, MAX_STATUS_ID, ROLE_STUDENT, ROLE_EMPLOYER
from app.database import get_db
from app.models import Application, ApplicationStatus, Vacancy
from app.schemas import ApplicationCreate, ApplicationResponse
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/applications", tags=["Заявки"])


# схема для обновления статуса
class StatusUpdate(BaseModel):
    status_id: int = Field(ge=MIN_STATUS_ID, le=MAX_STATUS_ID)


# преобразуем заявку в ответ
def app_to_response(a):
    return ApplicationResponse(
        id=a.id,
        vacancy_id=a.vacancy_id,
        vacancy_title=a.vacancy.title if a.vacancy else None,
        cover_letter=a.cover_letter,
        status_id=a.status_id,
        status_name=a.status.name if a.status else None,
        user_name=a.user.name if a.user else None,
        user_email=a.user.email if a.user else None,
        user_faculty=a.user.faculty.name if a.user and a.user.faculty else None,
        created_at=a.created_at,
    )


# подать заявку на вакансию (только студент)
@router.post("/", response_model=ApplicationResponse)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # только студенты могут подавать заявки
    if current_user.role != ROLE_STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут подавать заявки",
        )

    # проверяем существует ли вакансия
    vacancy = db.query(Vacancy).filter(Vacancy.id == data.vacancy_id).first()
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вакансия не найдена",
        )

    # проверяем нет ли уже заявки
    existing = (
        db.query(Application)
        .filter(
            Application.user_id == current_user.id,
            Application.vacancy_id == data.vacancy_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже подали заявку на эту вакансию",
        )

    # берём первый статус (На рассмотрении)
    default_status = db.query(ApplicationStatus).first()
    if not default_status:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Статусы заявок не настроены",
        )

    new_app = Application(
        user_id=current_user.id,
        vacancy_id=data.vacancy_id,
        status_id=default_status.id,
        cover_letter=data.cover_letter,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return app_to_response(new_app)


# получить свои заявки
@router.get("/my", response_model=list[ApplicationResponse])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # только свои заявки
    apps = db.query(Application).filter(Application.user_id == current_user.id).all()
    return [app_to_response(a) for a in apps]


# получить заявки на вакансию (только работодатель)
@router.get("/vacancy/{vacancy_id}", response_model=list[ApplicationResponse])
def get_vacancy_applications(
    vacancy_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != ROLE_EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только работодатели могут просматривать заявки на вакансии",
        )

    apps = db.query(Application).filter(Application.vacancy_id == vacancy_id).all()
    return [app_to_response(a) for a in apps]


# обновить статус заявки (только работодатель)
@router.put("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != ROLE_EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только работодатели могут менять статус заявки",
        )

    # ищем заявку
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )

    # проверяем что статус существует
    new_status = (
        db.query(ApplicationStatus)
        .filter(ApplicationStatus.id == data.status_id)
        .first()
    )
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статус не найден",
        )

    app.status_id = data.status_id
    db.commit()
    db.refresh(app)

    return app_to_response(app)


# удалить свою заявку (только студент)
@router.delete("/{application_id}")
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != ROLE_STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут удалять заявки",
        )

    # ищем заявку
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )

    # проверяем что это своя заявка
    if app.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно удалять только свои заявки",
        )

    db.delete(app)
    db.commit()

    return {"detail": "Заявка удалена"}

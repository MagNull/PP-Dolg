from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Skill, Faculty, ApplicationStatus, Review, Vacancy
from app.schemas import (
    CategoryResponse,
    SkillResponse,
    FacultyResponse,
    ReviewCreate,
    ReviewResponse,
)
from app.routes.auth import get_current_user
from app.models import User

# справочники и отзывы о вакансиях
router = APIRouter(prefix="/api", tags=["catalog"])


# справочник категорий
@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories


# справочник навыков
@router.get("/skills", response_model=list[SkillResponse])
def get_skills(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    return skills


# справочник факультетов
@router.get("/faculties", response_model=list[FacultyResponse])
def get_faculties(db: Session = Depends(get_db)):
    faculties = db.query(Faculty).all()
    return faculties


# справочник статусов заявок
@router.get("/statuses")
def get_statuses(db: Session = Depends(get_db)):
    statuses = db.query(ApplicationStatus).all()
    return [{"id": s.id, "name": s.name} for s in statuses]


# оставить отзыв о вакансии
@router.post("/reviews", response_model=ReviewResponse)
def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # проверяем что вакансия существует
    vacancy = db.query(Vacancy).filter(Vacancy.id == review_data.vacancy_id).first()
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вакансия не найдена"
        )

    # создаём отзыв
    new_review = Review(
        user_id=current_user.id,
        vacancy_id=review_data.vacancy_id,
        rating=review_data.rating,
        text=review_data.text,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return ReviewResponse(
        id=new_review.id,
        user_name=current_user.name,
        rating=new_review.rating,
        text=new_review.text,
        created_at=new_review.created_at,
    )


# отзывы о вакансии
@router.get("/reviews/vacancy/{vacancy_id}", response_model=list[ReviewResponse])
def get_vacancy_reviews(vacancy_id: int, db: Session = Depends(get_db)):
    # проверяем что вакансия существует
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вакансия не найдена"
        )

    reviews = db.query(Review).filter(Review.vacancy_id == vacancy_id).all()
    return [
        ReviewResponse(
            id=r.id,
            user_name=r.user.name if r.user else None,
            rating=r.rating,
            text=r.text,
            created_at=r.created_at,
        )
        for r in reviews
    ]

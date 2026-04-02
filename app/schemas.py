from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional, Literal
from datetime import datetime

from app.config import (
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH,
    MIN_COMPANY_NAME_LENGTH,
    MAX_COMPANY_NAME_LENGTH,
    ROLE_STUDENT,
    ROLE_EMPLOYER,
    EMPLOYMENT_TYPE_INTERNSHIP,
    EMPLOYMENT_TYPE_PART_TIME,
    EMPLOYMENT_TYPE_FULL_TIME,
    MIN_VACANCY_TITLE_LENGTH,
    MAX_VACANCY_TITLE_LENGTH,
    MIN_VACANCY_DESCRIPTION_LENGTH,
    MAX_VACANCY_DESCRIPTION_LENGTH,
    MAX_SALARY,
    MAX_COVER_LETTER_LENGTH,
    MIN_REVIEW_TEXT_LENGTH,
    MAX_REVIEW_TEXT_LENGTH,
    MIN_RATING,
    MAX_RATING,
)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH
    )
    name: str = Field(min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    faculty_id: Optional[int] = Field(default=None, ge=1)
    role: Literal[ROLE_STUDENT, ROLE_EMPLOYER] = ROLE_STUDENT
    company_name: Optional[str] = Field(
        default=None,
        min_length=MIN_COMPANY_NAME_LENGTH,
        max_length=MAX_COMPANY_NAME_LENGTH,
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: str
    faculty_id: Optional[int]
    created_at: datetime
    employer_id: Optional[int] = None
    company_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class VacancyCreate(BaseModel):
    title: str = Field(
        min_length=MIN_VACANCY_TITLE_LENGTH, max_length=MAX_VACANCY_TITLE_LENGTH
    )
    description: str = Field(
        min_length=MIN_VACANCY_DESCRIPTION_LENGTH,
        max_length=MAX_VACANCY_DESCRIPTION_LENGTH,
    )
    employer_id: Optional[int] = None  # берётся из JWT, не обязательно
    category_id: int = Field(ge=1)
    employment_type: Literal[
        EMPLOYMENT_TYPE_INTERNSHIP,
        EMPLOYMENT_TYPE_PART_TIME,
        EMPLOYMENT_TYPE_FULL_TIME,
    ]
    salary_from: Optional[int] = Field(default=None, ge=0, le=MAX_SALARY)
    salary_to: Optional[int] = Field(default=None, ge=0, le=MAX_SALARY)
    skill_ids: Optional[list[int]] = None

    # проверяем что salary_to >= salary_from
    @model_validator(mode="after")
    def check_salary_range(self):
        if self.salary_from is not None and self.salary_to is not None:
            if self.salary_to < self.salary_from:
                raise ValueError(
                    "Максимальная зарплата не может быть меньше минимальной"
                )
        return self


class VacancyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    employment_type: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    is_active: bool
    created_at: datetime
    employer_name: Optional[str] = None
    category_name: Optional[str] = None
    skills: list = []
    my_status_id: Optional[int] = None
    my_status_name: Optional[str] = None


class ApplicationCreate(BaseModel):
    vacancy_id: int = Field(ge=1)
    cover_letter: Optional[str] = Field(
        default=None, max_length=MAX_COVER_LETTER_LENGTH
    )


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vacancy_id: int
    vacancy_title: Optional[str] = None
    cover_letter: Optional[str]
    status_id: Optional[int] = None
    status_name: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_faculty: Optional[str] = None
    created_at: datetime


class ReviewCreate(BaseModel):
    vacancy_id: int = Field(ge=1)
    rating: int = Field(ge=MIN_RATING, le=MAX_RATING)
    text: str = Field(
        min_length=MIN_REVIEW_TEXT_LENGTH, max_length=MAX_REVIEW_TEXT_LENGTH
    )


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_name: Optional[str] = None
    rating: int
    text: Optional[str]
    created_at: datetime


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class FacultyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class VacancyListResponse(BaseModel):
    items: list[VacancyResponse]
    total: int

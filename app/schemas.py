from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional, Literal
from datetime import datetime

# схемы валидации данных


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    name: str = Field(min_length=2, max_length=100)
    faculty_id: Optional[int] = Field(default=None, ge=1)
    role: Literal["student", "employer"] = "student"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: str
    faculty_id: Optional[int]
    created_at: datetime
    employer_id: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class VacancyCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=5000)
    employer_id: Optional[int] = None  # берётся из JWT, не обязательно
    category_id: int = Field(ge=1)
    employment_type: Literal["internship", "part_time", "full_time"]
    salary_from: Optional[int] = Field(default=None, ge=0, le=1000000)
    salary_to: Optional[int] = Field(default=None, ge=0, le=1000000)

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


class ApplicationCreate(BaseModel):
    vacancy_id: int = Field(ge=1)
    cover_letter: str = Field(min_length=10, max_length=2000)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vacancy_id: int
    vacancy_title: Optional[str] = None
    cover_letter: Optional[str]
    status_name: Optional[str] = None
    created_at: datetime


class ReviewCreate(BaseModel):
    vacancy_id: int = Field(ge=1)
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=5, max_length=1000)


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

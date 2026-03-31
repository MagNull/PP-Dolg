from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base, engine

# модели базы данных


# пользователь
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), default="student")
    faculty_id = Column(Integer, ForeignKey("faculties.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    faculty = relationship("Faculty", back_populates="users")
    employer = relationship("Employer", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user")
    skills = relationship("UserSkill", back_populates="user")
    reviews = relationship("Review", back_populates="user")


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    users = relationship("User", back_populates="faculty")


# работодатель
class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="employer")
    vacancies = relationship("Vacancy", back_populates="employer")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    vacancies = relationship("Vacancy", back_populates="category")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    vacancies = relationship("VacancySkill", back_populates="skill")
    users = relationship("UserSkill", back_populates="skill")


# вакансия
class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("employers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    employment_type = Column(
        String(20), nullable=False
    )  # internship, part_time, full_time
    salary_from = Column(Integer, nullable=True)
    salary_to = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employer = relationship("Employer", back_populates="vacancies")
    category = relationship("Category", back_populates="vacancies")
    skills = relationship("VacancySkill", back_populates="vacancy")
    applications = relationship("Application", back_populates="vacancy")
    reviews = relationship("Review", back_populates="vacancy")


class VacancySkill(Base):
    __tablename__ = "vacancy_skills"

    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    __table_args__ = (UniqueConstraint("vacancy_id", "skill_id"),)

    vacancy = relationship("Vacancy", back_populates="skills")
    skill = relationship("Skill", back_populates="vacancies")


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "skill_id"),)

    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="users")


class ApplicationStatus(Base):
    __tablename__ = "application_statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    applications = relationship("Application", back_populates="status")


# заявка на вакансию
class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("application_statuses.id"), nullable=False)
    cover_letter = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "vacancy_id"),)

    user = relationship("User", back_populates="applications")
    vacancy = relationship("Vacancy", back_populates="applications")
    status = relationship("ApplicationStatus", back_populates="applications")


# отзыв о вакансии
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    vacancy = relationship("Vacancy", back_populates="reviews")


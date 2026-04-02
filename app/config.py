# конфигурация приложения
import os
from typing import Final

# === База данных ===
DATABASE_URL: Final[str] = os.getenv("DATABASE_URL", "sqlite:///./campus_jobs.db")

# === JWT настройки ===
SECRET_KEY: Final[str] = os.getenv("SECRET_KEY", "секретный-ключ-для-jwt")
ALGORITHM: Final[str] = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 1440  # 24 часа

# === Приложение ===
APP_TITLE: Final[str] = "Работа в кампусе"
STATIC_DIR: Final[str] = "static"

# === Валидация ===
# Пароль
MIN_PASSWORD_LENGTH: Final[int] = 6
MAX_PASSWORD_LENGTH: Final[int] = 100

# Имя
MIN_NAME_LENGTH: Final[int] = 2
MAX_NAME_LENGTH: Final[int] = 100

# Email
MAX_EMAIL_LENGTH: Final[int] = 200

# Компания
MIN_COMPANY_NAME_LENGTH: Final[int] = 2
MAX_COMPANY_NAME_LENGTH: Final[int] = 200

# Вакансия
MIN_VACANCY_TITLE_LENGTH: Final[int] = 3
MAX_VACANCY_TITLE_LENGTH: Final[int] = 200
MIN_VACANCY_DESCRIPTION_LENGTH: Final[int] = 10
MAX_VACANCY_DESCRIPTION_LENGTH: Final[int] = 5000

# Зарплата
MAX_SALARY: Final[int] = 1_000_000

# Отклик
MAX_COVER_LETTER_LENGTH: Final[int] = 2000

# Отзыв
MIN_REVIEW_TEXT_LENGTH: Final[int] = 5
MAX_REVIEW_TEXT_LENGTH: Final[int] = 1000
MIN_RATING: Final[int] = 1
MAX_RATING: Final[int] = 5

# === Типы занятости ===
EMPLOYMENT_TYPE_INTERNSHIP: Final[str] = "internship"
EMPLOYMENT_TYPE_PART_TIME: Final[str] = "part_time"
EMPLOYMENT_TYPE_FULL_TIME: Final[str] = "full_time"
EMPLOYMENT_TYPES: Final[list[str]] = [
    EMPLOYMENT_TYPE_INTERNSHIP,
    EMPLOYMENT_TYPE_PART_TIME,
    EMPLOYMENT_TYPE_FULL_TIME,
]

# === Роли пользователей ===
ROLE_STUDENT: Final[str] = "student"
ROLE_EMPLOYER: Final[str] = "employer"
ROLES: Final[list[str]] = [ROLE_STUDENT, ROLE_EMPLOYER]

# === Пагинация ===
DEFAULT_PAGE_LIMIT: Final[int] = 100

# === Статус заявки ===
MIN_STATUS_ID: Final[int] = 1
MAX_STATUS_ID: Final[int] = 10

# === Хеширование ===
PWD_HASH_SCHEME: Final[str] = "bcrypt"

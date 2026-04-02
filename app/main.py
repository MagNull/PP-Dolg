import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# подключаем роутеры
from app.routes import auth, vacancies, applications, catalog

from app.config import APP_TITLE, STATIC_DIR, MIN_PASSWORD_LENGTH, MIN_NAME_LENGTH

# создаём приложение
app = FastAPI(title=APP_TITLE)


# обработчик ошибок валидации — возвращаем понятные сообщения
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        # собираем путь к полю (пропускаем "body")
        field = " → ".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append(
            {
                "поле": field,
                "сообщение": err["msg"],
                "тип_ошибки": err["type"],
            }
        )

    detail = "Проверьте введённые данные"
    if errors:
        first_error = errors[0]
        field = first_error["поле"]
        error_type = first_error["тип_ошибки"]

        if field == "email":
            detail = "Введите корректный email"
        elif field == "password" and "too_short" in error_type:
            detail = f"Пароль должен быть не короче {MIN_PASSWORD_LENGTH} символов"
        elif field == "name" and "too_short" in error_type:
            detail = f"Имя должно быть не короче {MIN_NAME_LENGTH} символов"
        elif "missing" in error_type:
            if field:
                detail = f"Заполните поле: {field}"
            else:
                detail = "Заполните обязательные поля"

    return JSONResponse(
        status_code=422,
        content={
            "detail": detail,
            "errors": errors,
        },
    )


# подключаем роутеры
app.include_router(auth.router)
app.include_router(vacancies.router)
app.include_router(applications.router)
app.include_router(catalog.router)

# создаём директорию для статики если её нет
os.makedirs(STATIC_DIR, exist_ok=True)

# раздаём статику
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


# создаём таблицы и заполняем БД при запуске
@app.on_event("startup")
def startup():
    from app.database import engine, Base, SessionLocal
    from app.seed import seed_database

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()

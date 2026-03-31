import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# подключаем роутеры
from app.routes import auth, vacancies, applications, catalog

# создаём приложение
app = FastAPI(title="Работа в кампусе")


# обработчик ошибок валидации — возвращаем понятные сообщения
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        # собираем путь к полю (пропускаем "body")
        field = " → ".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append({
            "поле": field,
            "сообщение": err["msg"],
            "тип_ошибки": err["type"],
        })
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Ошибка валидации данных",
            "errors": errors,
        },
    )


# подключаем роутеры
app.include_router(auth.router)
app.include_router(vacancies.router)
app.include_router(applications.router)
app.include_router(catalog.router)

# создаём директорию для статики если её нет
os.makedirs("static", exist_ok=True)

# раздаём статику
app.mount("/", StaticFiles(directory="static", html=True), name="static")


# создаём таблицы и заполняем БД при запуске
@app.on_event("startup")
def startup():
    from app.database import engine, Base, SessionLocal
    from app.seed import seed_database

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()

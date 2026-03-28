import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# подключаем роутеры
from app.routes import auth, vacancies, applications, catalog

# создаём приложение
app = FastAPI(title="Работа в кампусе")

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

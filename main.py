from fastapi import FastAPI

# главное приложение
app = FastAPI(title="Поиск работы в кампусе")


@app.get("/")
def index():
    return {"message": "Campus Jobs API"}

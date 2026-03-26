from fastapi import FastAPI

app = FastAPI(title="Поиск работы в кампусе")


@app.get("/")
def index():
    return {"message": "Campus Jobs API"}

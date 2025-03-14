from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import create_tables
from app.routers import recipes, meal_plans

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(recipes.router)
app.include_router(meal_plans.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
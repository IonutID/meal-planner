from fastapi import FastAPI
from app.db.database import create_tables
from app.routers import recipes, meal_plans

app = FastAPI()
app.include_router(recipes.router)
app.include_router(meal_plans.router)

@app.on_event("startup")
def startup_event():
    create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
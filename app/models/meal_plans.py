from pydantic import BaseModel

class MealPlanBase(BaseModel):
    name: str
    description: str

class MealPlanCreate(MealPlanBase):
    pass

class MealPlanUpdate(MealPlanBase):
    pass

class MealPlanInDBBase(MealPlanBase):
    id: int

    class Config:
        from_attributes = True  # Changed from orm_mode = True

class MealPlan(MealPlanInDBBase):
    pass

class MealPlanInDB(MealPlanInDBBase):
    pass

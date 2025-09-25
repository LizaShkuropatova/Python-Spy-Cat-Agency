from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class CatCreate(BaseModel):
    name: str
    years_of_experience: int
    breed: str
    salary: float

class CatRead(BaseModel):
    id: int
    name: str
    years_of_experience: int
    breed: str
    salary: float
    model_config = ConfigDict(from_attributes=True)

class CatUpdateSalary(BaseModel):
    salary: float

class CatUpdate(BaseModel):
    name: str
    years_of_experience: int
    breed: str
    salary: float

class TargetCreate(BaseModel):
    name: str
    country: str
    notes: str = ""
    completed: bool = False


class TargetRead(BaseModel):
    id: int
    name: str
    country: str
    notes: str
    completed: bool
    model_config = ConfigDict(from_attributes=True)

class TargetNotesUpdate(BaseModel):
    notes: str = Field(min_length=1)

class TargetCompletedUpdate(BaseModel):
    completed: bool

class MissionCreate(BaseModel):
    targets: List[TargetCreate] = Field(min_length=1, max_length=3)

class AssignCatMission(BaseModel):
    cat_id: int

class MissionRead(BaseModel):
    id: int
    cat_id: Optional[int]
    completed: bool
    targets: List[TargetRead]
    model_config = ConfigDict(from_attributes=True)



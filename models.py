from typing import Optional, List
from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship


class Cat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    years_of_experience: int
    breed: str
    salary: float
    missions: List["Mission"] = Relationship(back_populates="cat")

class Target(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mission_id: int = Field(foreign_key="mission.id", index=True)
    name: str
    country: str
    notes: str = ""
    completed: bool = False

    # Targets don't repeat for the 1 mission
    __table_args__ = (
        UniqueConstraint("mission_id", "name", name="uq_mission_target_name"),
    )

class Mission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cat_id: Optional[int] = Field(default=None, foreign_key="cat.id")
    completed: bool = False
    cat: Optional[Cat] = Relationship(back_populates="missions")

    # if del mission -> del all Targets
    targets: List[Target] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


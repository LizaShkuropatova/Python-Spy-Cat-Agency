from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from models import Cat
from schemas import CatCreate, CatRead, CatUpdateSalary
from cat_api import validate_breed
from db import get_session

router = APIRouter(prefix="/cats", tags=["cats"])

@router.post("/", response_model=CatRead, status_code=status.HTTP_201_CREATED, summary="Create a Cat")
async def create_cat(body: CatCreate, session: Session = Depends(get_session)):
    await validate_breed(body.breed) # breed from api
    cat = Cat(**body.model_dump())
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat

@router.get("", response_model=list[CatRead], summary="List of Cats")
def list_cats(session: Session = Depends(get_session)):
    return session.exec(select(Cat)).all()


@router.get("/{cat_id}", response_model=CatRead, summary="Find a Cat by id")
def get_cat(cat_id: int, session: Session = Depends(get_session)):
    cat = session.get(Cat, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    return cat


@router.patch("/{cat_id}", response_model=CatRead, summary="Update Cats’ Salary")
def update_cat_salary(cat_id: int, body: CatUpdateSalary, session: Session = Depends(get_session)):
    cat = session.get(Cat, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    cat.salary = body.salary
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat

@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cat(cat_id: int, session: Session = Depends(get_session)):
    cat = session.get(Cat, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    session.delete(cat)
    session.commit()
    return
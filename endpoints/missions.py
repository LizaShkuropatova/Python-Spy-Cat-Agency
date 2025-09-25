from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from db import get_session

from models import Mission, Target, Cat
from schemas import MissionCreate, MissionRead, TargetNotesUpdate, TargetCompletedUpdate, TargetRead, AssignCatMission

router = APIRouter(prefix="/missions", tags=["missions"])

@router.post("/", response_model=MissionRead, status_code=status.HTTP_201_CREATED, summary="Create a Mission with Targets (without a cat)")
def create_mission(body: MissionCreate, session: Session = Depends(get_session)):
    mission = Mission(completed=False)
    session.add(mission)
    session.commit()
    session.refresh(mission)

    for t in body.targets:
        target = Target(
            mission_id=mission.id,
            name=t.name,
            country=t.country,
            notes=t.notes or "",
            completed=bool(t.completed),
        )
        session.add(target)

    session.commit()
    session.refresh(mission)
    return mission


@router.get("", response_model=list[MissionRead], summary="List Missions")
def list_missions(session: Session = Depends(get_session)):
    missions = session.exec(select(Mission)).all()
    return missions


@router.get("/{mission_id}", response_model=MissionRead, summary="Get Mission by id")
def get_mission(mission_id: int, session: Session = Depends(get_session)):
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Mission (if not assigned to a Cat)")
def delete_mission(mission_id: int, session: Session = Depends(get_session)):
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.cat_id is not None:
        raise HTTPException(
            status_code=409,
            detail="Mission already assigned to a cat and cannot be deleted",
        )
    session.delete(mission)
    session.commit()
    return


@router.patch("/{mission_id}/assign", response_model=MissionRead, summary="Assign a Cat to Mission")
def assign_cat_to_mission(
    mission_id: int,
    body: AssignCatMission,
    session: Session = Depends(get_session),
):
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.cat_id is not None:
        raise HTTPException(status_code=409, detail="Mission already assigned to a cat")

    cat = session.get(Cat, body.cat_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Cat not found")


    existing_active = session.exec(
        select(Mission).where(Mission.cat_id == cat.id, Mission.completed == False)
    ).first()
    if existing_active:
        raise HTTPException(status_code=409, detail="Cat already has an active mission")

    mission.cat_id = cat.id
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


def get_mission_and_target(session: Session, mission_id: int, target_id: int) -> tuple[Mission, Target]:
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    target = session.get(Target, target_id)
    if target is None or target.mission_id != mission.id:
        raise HTTPException(status_code=404, detail="Target not found in mission")
    return mission, target

def check_mission_completed(session: Session, mission: Mission) -> None:
    targets = session.exec(select(Target).where(Target.mission_id == mission.id)).all()
    mission.completed = bool(targets) and all(t.completed for t in targets)
    session.add(mission)
    session.commit()
    session.refresh(mission)


@router.patch("/{mission_id}/targets/{target_id}/completed", response_model=TargetRead, summary="Update targets as completed")
def set_target_completed(
    mission_id: int,
    target_id: int,
    body: TargetCompletedUpdate,
    session: Session = Depends(get_session)):

    mission, target = get_mission_and_target(session, mission_id, target_id)

    target.completed = bool(body.completed)
    session.add(target)
    session.commit()
    session.refresh(target)

    check_mission_completed(session, mission)

    return target


@router.patch(
    "/{mission_id}/targets/{target_id}/notes",
    response_model=TargetRead,
    summary="Update target notes (frozen if target or mission is completed)",
)
def update_target_notes(
    mission_id: int,
    target_id: int,
    body: TargetNotesUpdate,
    session: Session = Depends(get_session),
):
    mission, target = get_mission_and_target(session, mission_id, target_id)

    # can't change notes if the targets or missions has been completed
    if mission.completed or target.completed:
        raise HTTPException(
            status_code=409,
            detail="Notes are frozen because target or mission is completed",
        )

    target.notes = body.notes
    session.add(target)
    session.commit()
    session.refresh(target)
    return target
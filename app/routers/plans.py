from fastapi import APIRouter, status

from sqlmodel import select
from models import Plan, PlanCreate
from db import SessionDep


router = APIRouter(tags=["plans"])


@router.get("/plans", response_model=list[Plan])
async def list_plans(session: SessionDep):
    plans = session.exec(select(Plan)).all()
    return plans


@router.post("/plans", response_model=Plan, status_code=status.HTTP_201_CREATED)
async def create_plan(plan_data: PlanCreate, session: SessionDep):
    plan = Plan.model_validate(plan_data.model_dump())
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan

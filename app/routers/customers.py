from fastapi import APIRouter, HTTPException, status, Query

from sqlmodel import select
from models import (
    Customer,
    CustomerCreate,
    CustomerUpdate,
    Plan,
    CustomerPlan,
    StatusEnum,
)
from db import SessionDep


router = APIRouter(tags=["customers"])


@router.get("/customers", response_model=list[Customer])
async def list_customers(session: SessionDep):
    return session.exec(select(Customer)).all()


@router.post("/customers", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.get("/customers/{customer_id}", response_model=Customer)
async def read_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    return customer


@router.patch(
    "/customers/{customer_id}",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
)
async def update_customer(
    customer_id: int, customer_data: CustomerUpdate, session: SessionDep
):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    customer_data_dict = customer_data.model_dump(exclude_unset=True)
    customer.sqlmodel_update(customer_data_dict)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    session.delete(customer)
    session.commit()
    return {"detail": "ok"}


@router.get("/customers/{customer_id}/plans")
async def list_customer_plans(
    customer_id: int, session: SessionDep, plan_status: StatusEnum = Query()
):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    query = (
        select(CustomerPlan)
        .where(CustomerPlan.customer_id == customer.id)
        .where(CustomerPlan.status == plan_status)
    )
    plans = session.exec(query).all()
    return plans


@router.post("/customers/{customer_id}/plans/{plan_id}", response_model=CustomerPlan)
async def subscribe_customer_to_plan(
    customer_id: int,
    plan_id: int,
    session: SessionDep,
    plan_status: StatusEnum = Query(),
):
    customer = session.get(Customer, customer_id)
    plan = session.get(Plan, plan_id)
    if customer is None or plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer or plan not found"
        )
    customer_plan = CustomerPlan(
        plan_id=plan.id, customer_id=customer.id, status=plan_status
    )
    session.add(customer_plan)
    session.commit()
    session.refresh(customer_plan)
    return customer_plan

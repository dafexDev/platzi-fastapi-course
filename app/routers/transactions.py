from typing import List

from fastapi import APIRouter, HTTPException, status

from sqlmodel import select
from models import Customer, Transaction, TransactionCreate, TransactionUpdate
from db import SessionDep


router = APIRouter(tags=["transactions"])


@router.get("/transactions", response_model=List[Transaction])
async def list_transactions(session: SessionDep):
    transactions = session.exec(select(Transaction)).all()
    return transactions


@router.post(
    "/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED
)
async def create_transaction(transaction_data: TransactionCreate, session: SessionDep):
    transaction_data_dict = transaction_data.model_dump()
    customer = session.get(Customer, transaction_data_dict.get("customer_id"))
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    transaction = Transaction.model_validate(transaction_data_dict)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def read_transaction(transaction_id: int, session: SessionDep):
    transaction = session.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    return transaction


@router.patch(
    "/transactions/{transaction_id}",
    response_model=Transaction,
    status_code=status.HTTP_201_CREATED,
)
async def update_transaction(
    transaction_id: int, transaction_data: TransactionUpdate, session: SessionDep
):
    transaction = session.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    transaction_data_dict = transaction_data.model_dump(exclude_unset=True)
    transaction.sqlmodel_update(transaction_data_dict)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int, session: SessionDep):
    transaction = session.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    session.delete(transaction)
    session.commit()
    return {"detail": "ok"}

from typing import Optional, List

from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field, Relationship


class CustomerPlan(SQLModel, table=True):
    id: int = Field(primary_key=True)
    plan_id: int = Field(foreign_key="plan.id")
    customer: int = Field(foreign_key="customer.id")


class Plan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    price: int = Field(default=None)
    description: str = Field(default=None)
    customers: List["Customer"] = Relationship(
        back_populates="plans", link_model=CustomerPlan
    )


class CustomerBase(SQLModel):
    name: str = Field(default=None)
    description: Optional[str] = Field(default=None)
    email: EmailStr = Field(default=None)
    age: int = Field(default=None)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class Customer(CustomerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(back_populates="customer")
    plans: List[Plan] = Relationship(
        back_populates="customers", link_model=CustomerPlan
    )


class TransactionBase(SQLModel):
    amount: int = Field(default=None)
    description: str = Field(default=None)


class TransactionCreate(TransactionBase):
    customer_id: int = Field(foreign_key="customer.id")
    

class TransactionUpdate(TransactionBase):
    pass


class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    customer: Customer = Relationship(back_populates="transactions")


class Invoice(BaseModel):
    id: int
    customer: Customer
    transactions: List[Transaction]
    total: int

    @property
    def ammount_total(self):
        return sum(transaction.amount for transaction in self.transactions)

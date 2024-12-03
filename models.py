from typing import Optional, List
from pydantic import BaseModel, EmailStr


class Customer(BaseModel):
    id: int
    name: str
    description: Optional[str]
    email: EmailStr
    age: int


class Transaction(BaseModel):
    id: int
    amount: int
    description: str


class Invoice(BaseModel):
    id: int
    customer: Customer
    transactions: List[Transaction]
    total: int

    @property
    def ammount_total(self):
        return sum(transaction.amount for transaction in self.transactions)

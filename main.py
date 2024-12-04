from fastapi import FastAPI, HTTPException
from typing import Literal, Optional, List
from datetime import datetime
import pytz

from models import Customer, CustomerCreate, CustomerUpdate, Transaction, Invoice
from db import SessionDep, create_all_tables
from sqlmodel import select


app = FastAPI(lifespan=create_all_tables)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Argentina/Buenos_Aires",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}

time_formats = ("12", "24")


def get_current_time_in_timezone(
    iso_code: str,
    time_format: Optional[str] = "24",
) -> str:
    if iso_code not in country_timezones:
        raise ValueError("Invalid ISO Code")
    if time_format not in time_formats:
        raise ValueError("Invalid time format")

    timezone_name = country_timezones[iso_code]
    timezone = pytz.timezone(timezone_name)
    now = datetime.now(timezone)

    if time_format == "12":
        return now.strftime("%I:%M:%S %p")
    return now.strftime("%H:%M:%S")


@app.get("/time/{iso_code}")
async def time_in_timezone(
    iso_code: Literal["CO", "MX", "AR", "BR", "PE"],
    time_format: Optional[Literal["12", "24"]] = "24",
):
    iso_code = iso_code.upper()
    try:
        current_time_in_timezone = get_current_time_in_timezone(iso_code, time_format)
        return {"time": current_time_in_timezone}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail="Invalid timezone")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@app.get("/customers", response_model=List[Customer])
async def list_customers(session: SessionDep):
    return session.exec(select(Customer)).all()


@app.get("/customers/{customer_id}", response_model=Customer)
async def read_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.patch("/customers/{customer_id}", response_model=Customer, status_code=201)
async def update_customer(
    customer_id: int, customer_data: CustomerUpdate, session: SessionDep
):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer_data_dict = customer_data.model_dump(exclude_unset=True)
    customer.sqlmodel_update(customer_data_dict)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@app.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    session.delete(customer)
    session.commit()
    return {"detail": "ok"}


@app.post("/transactions")
async def create_transaction(transaction_data: Transaction):
    return transaction_data


@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data

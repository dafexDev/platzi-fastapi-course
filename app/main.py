from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated, Literal, Optional
from datetime import datetime
import pytz
import time

from db import create_all_tables

from .routers import customers, transactions, invoices, plans


app = FastAPI(lifespan=create_all_tables)
app.include_router(customers.router)
app.include_router(transactions.router)
app.include_router(invoices.router)
app.include_router(plans.router)


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request: {request.url} completed in: {process_time:.4f} seconds")
    return response


@app.middleware("http")
async def print_request_headers(request: Request, call_next):
    print(f"Request {request.url} headers")
    for header, value in request.headers.items():
        print(f"\t{header}: {value}")
    return await call_next(request)


security = HTTPBasic()


@app.get("/")
async def root(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    print(credentials)
    if credentials.username == "dafex" and credentials.password == "password":
        return {"message": "Hello, World!"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid timezone"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

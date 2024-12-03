from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime
import pytz


class Customer(BaseModel):
    name: str
    description: Optional[str]
    email: str
    age: int


app = FastAPI()


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


@app.post("/customers")
async def create_customers(customer_data: Customer):
    return customer_data

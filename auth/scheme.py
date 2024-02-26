from datetime import datetime, date
from typing import Union

from pydantic import BaseModel


class UserData(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password1: str
    password2: str
    phone: str
    image: str
    birth_date: date


class UserInDb(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    phone: str
    image: str
    birth_date: datetime


class UserInfo(BaseModel):
    first_name: str
    last_name: str
    username: str
    phone: str
    birth_date: datetime


class UserLogin(BaseModel):
    username: str
    password: str
    email: str


class ForgetPasswordRequest(BaseModel):
    email: str


class CityAddScheme(BaseModel):
    name: str
    country: int


class CountryScheme(BaseModel):
    id: int
    name: str
    code: str


class CityScheme(BaseModel):
    id: int
    name: str
    country: CountryScheme


class AddressScheme(BaseModel):
    id: int
    name: str
    city: CityScheme
    country: CountryScheme


class AddressPOSTScheme(BaseModel):
    name: str
    city_id: int
    country_id: int




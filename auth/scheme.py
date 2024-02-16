from datetime import datetime, date
from pydantic import BaseModel


class User(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password1: str
    password2: str
    phone: str
    image: str
    birth_date: date

class User_in_db(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    phone: str
    image: str
    birth_date: datetime

class User_Info(BaseModel):
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
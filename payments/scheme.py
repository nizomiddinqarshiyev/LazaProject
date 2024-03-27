from datetime import datetime
from typing import List, Union
from decimal import Decimal
from fastapi import UploadFile
from pydantic import BaseModel, Field
from .utils import decode_card_number


class UserCardScheme(BaseModel):
    card_number: str = Field(max_length=16, min_length=16)
    card_expiration: str = Field(max_length=4, min_length=4)
    card_cvc: Union[str, None]


class CardScheme(BaseModel):
    id: int
    card_number: str
    card_expiration: str


class CreateInvoiceScheme(BaseModel):
    amount: int
    order_id: int

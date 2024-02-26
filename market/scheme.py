from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List,Union


class ShoppingCartScheme(BaseModel):
    id: int
    product: dict
    count: int
    added_at: datetime


class ShoppingSaveCartScheme(BaseModel):
    product_id: int
    count: Union[int, None] = Field(gte=0)


class ShippingAddressScheme(BaseModel):
    shipping_address: str


class ShippingAddressGetScheme(BaseModel):
    id: int
    shipping_address: str
    user_id: int


class UserCardScheme(BaseModel):
    card_number: str = Field(max_length=16, min_length=16)
    card_expiration: str = Field(max_length=4, min_length=4)
    card_cvc: Union[int ,None] = None


class CardScheme(BaseModel):
    id: int
    card_number: str
    card_expiration: str


class OrderSchema(BaseModel):
    product_id: int
    tracking_number: Optional[str]
    status: str
    payment_method: str
    shipping_address_id: int
    delivery_method_id: int
    user_card_id: Optional[int]




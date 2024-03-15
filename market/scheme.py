from datetime import datetime
from pydantic import conint
from typing import Optional, List
from typing import Union

from pydantic import BaseModel, Field


class ShoppingCartSchemas(BaseModel):
    product: dict
    order_id: int
    count: int
    added_at: datetime
    subtotal: float
    shipping_cost: float
    total: float


class ShoppingCountCartSchemas(BaseModel):
    product_ids: int
    count: Optional[conint(gt=0)]


class ShoppingSaveCartSchemas(BaseModel):
    product_ids: int


class ShippingAddressSchemas(BaseModel):
    shipp_address: str

class ShippingAddressGetSchemas(BaseModel):
    id: int
    shipp_address: str
    user_ids: int


class UserCardSchemas(BaseModel):
    card_numbers: str = Field(max_length=16, min_length=16)
    card_expiration: str = Field(max_length=4, min_length=4)
    cvc: Optional[int] = None


class UserCardDelete(BaseModel):
    card: int


class CardSchemas(BaseModel):
    user_name: dict
    cards: List[dict]


class OrderSchemas(BaseModel):

    product_ids: int
    tracking_numbers: Optional[str]
    status: str
    payment_method: str
    shipp_address_id: int
    delivery_method_id: int
    user_card_id: Optional[int]


class ReviewCreate(BaseModel):
    message: Union[str, None]
    product_id: int
    star: float


class ReviewGet(BaseModel):
    id: int
    message: str
    user_id: int
    product_id: int
    star: float


class LikeScheme(BaseModel):
    product_id: int


class LikeGet(BaseModel):
    id: int
    user_id: int
    product: int
    description: str
    title: str


class WishlistScheme(BaseModel):
    product_id: int


class WishlistGet(BaseModel):
    id: int
    user_id: int
    product_id: int


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
from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class get_product_list(BaseModel):
    id: int
    brand_id: int
    name: str
    price: float
    quantity: int
    created_at: datetime
    sold_quantity: int
    description: str
    category_id: int
    subcategory_id: int


class add_product(BaseModel):
    name: str
    brand_id: int
    price: float
    quantity: int
    description: str
    category_id: int
    subcategory_id: int


class get_category(BaseModel):
    id:int
    name:str

class add_category(BaseModel):
    name :str


class subcategroy_list(BaseModel):
    id:int
    name:str
    category_id:int


class Add_subcategory(BaseModel):
    name:str
    category_id:int

from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from sqlalchemy import Date, DateTime, TIMESTAMP


class get_category(BaseModel):
    id: int
    name: str


class subcategroy_list(BaseModel):
    id: int
    name: str
    category_id: get_category


class subcategroy_list_for_product(BaseModel):
    id: int
    name: str
    category_id: int


class Brands(BaseModel):
    id: int
    name: str


class get_product_list(BaseModel):
    id: int
    brand_id: Brands
    name: str
    price: float
    quantity: int
    created_at: datetime
    sold_quantity: int
    description: str
    category_id: get_category
    subcategory_id: subcategroy_list_for_product


class get_product_list_for_productcolor(BaseModel):
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


class add_category(BaseModel):
    name: str


class Add_subcategory(BaseModel):
    name: str
    category_id: int


class BrandsAdd(BaseModel):
    name: str


class Colors(BaseModel):
    id: int
    code: str


class ColorsAdd(BaseModel):
    code: str


class ProductColors(BaseModel):
    id: int
    product_id: get_product_list_for_productcolor
    color_id: Colors


class Discounts(BaseModel):
    id: int
    title: str
    discount: int
    created_at: datetime
    start_date: datetime
    end_date: datetime


class DiscountsAdd(BaseModel):
    title: str
    discount: int
    start_date: datetime
    end_date: datetime


class Product_Discount(BaseModel):
    id:int
    product_id:int
    discount_id:int
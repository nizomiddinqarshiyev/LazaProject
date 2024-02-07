from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    Text, TIMESTAMP, DECIMAL, UniqueConstraint,
    Enum, MetaData, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()
metadata = MetaData()


class User(Base):
    __tablename__ = 'user'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(30))
    lastname = Column(String(30))
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    phone = Column(Integer)
    address = Column(Integer, ForeignKey('address.id'))
    image = Column(String)
    is_verified = Column(Boolean)
    registration_at = Column(TIMESTAMP, default=datetime.utcnow)
    birth_date = Column(TIMESTAMP, nullable=True)


class CategoryEnum(enum.Enum):
    men = 'Men'
    women = 'Women'
    kids = 'Kids'


class Category(Base):
    __tablename__ = 'category'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class Subcategory(Base):
    __tablename__ = 'subcategory'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category")
    UniqueConstraint('name', 'category_id', name='uniqNS')


class Brand(Base):
    __tablename__ = 'brand'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class Color(Base):
    __tablename__ = 'color'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(length=7))


class ProductColor(Base):
    __tablename__ = 'ProductColor'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    color_id = Column(Integer, ForeignKey('color.id'))


class Size(Base):
    __tablename__ = 'size'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    size = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category")


class ProductSize(Base):
    __tablename__ = 'product_size'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    size_id = Column(Integer, ForeignKey('size.id'))


class Product(Base):
    __tablename__ = 'product'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey('brand.id'))
    name = Column(String)
    price = Column(DECIMAL(precision=10, scale=2))
    quantity = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    sold_quantity = Column(Integer, default=0)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('category.id'))
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'))
    category = Column(Enum(CategoryEnum))


class Discount(Base):
    __tablename__ = 'discount'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    discount = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    start_date = Column(TIMESTAMP)
    end_date = Column(TIMESTAMP)


class ProductDiscount(Base):
    __tablename__ = 'product_discount'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    discount_id = Column(Integer, ForeignKey('discount.id'))


class File(Base):
    __tablename__ = 'file'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    file = Column(String)
    product_id = Column(Integer, ForeignKey('product.id'))
    hash = Column(String, unique=True)


class StatusEnum(enum.Enum):
    delivered = 'delivered'
    processing = 'processing'
    canceled = 'canceled'


class PaymentMethodEnum(enum.Enum):
    cash = 'cash'
    card = 'card'


class Order(Base):
    __tablename__ = 'order'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_number = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
    ordered_at = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(Enum(StatusEnum))
    payment_method = Column(Enum(PaymentMethodEnum))
    shipping_address_id = Column(Integer, ForeignKey('shipping_address.id'))
    delivery_method_id = Column(Integer, ForeignKey('delivery_method.id'))
    user_card_id = Column(Integer, ForeignKey('user_card.id'), nullable=True)


class ProductOrder(Base):
    __tablename__ = 'product_order'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    order_id = Column(Integer, ForeignKey('order.id'))


class ShippingAddress(Base):
    __tablename__ = 'shipping_address'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    shipping_address = Column(Text)


class City(Base):
    __tablename__ = 'city'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    country = Column(Integer, ForeignKey('country.id'))


class Country(Base):
    __tablename__ = 'country'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    code = Column(String)


class Address(Base):
    __tablename__ = 'address'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('city.id'))
    country_id = Column(Integer, ForeignKey('country.id'))


class DeliveryMethod(Base):
    __tablename__ = 'delivery_method'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_company = Column(String)
    delivery_day = Column(String)
    delivery_price = Column(DECIMAL(precision=10, scale=2))


class UserCard(Base):
    __tablename__ = 'user_card'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_number = Column(String)
    card_expiration = Column(String)
    cvc = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))


class Review(Base):
    __tablename__ = 'review'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    star = Column(DECIMAL(precision=10, scale=1))
    reviewed_at = Column(TIMESTAMP, default=datetime.utcnow)


class Image(Base):
    __tablename__ = 'image_review'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(String)
    review_id = Column(Integer, ForeignKey('review.id'))


class ShoppingCart(Base):
    __tablename__ = 'shopping_cart'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    count = Column(Integer, default=1)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    UniqueConstraint('user_id', 'product_id', name='uniqueSC')


class BankCard(Base):
    __tablename__ = 'bank_card'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_number = Column(String(length=32))
    card_expiration = Column(String(length=4))
    card_cvc = Column(String(length=3), nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    token = Column(String, nullable=True)


class PromoCode(Base):
    __tablename__ = 'promo_code'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    promo_code = Column(String)
    price = Column(DECIMAL(precision=10, scale=2))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    end_at = Column(TIMESTAMP)
    start_at = Column(TIMESTAMP)


class UsedPromoCode(Base):
    __tablename__ = 'used_promo_code'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    promo_code_id = Column(Integer, ForeignKey('promo_code.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    used_at = Column(TIMESTAMP, default=datetime.utcnow)


class Role(Base):
    __tablename__ = 'role'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), unique=True)


class UserRole(Base):
    __tablename__ = 'user_role'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    role_id = Column(Integer, ForeignKey('role.id'))
    chat_id = Column(Integer)


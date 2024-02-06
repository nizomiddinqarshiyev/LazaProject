from sqlalchemy import Column, ForeignKey, Integer, String, Text, TIMESTAMP, DECIMAL, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()


class CategoryEnum(enum.Enum):
    men = 'Men'
    women = 'Women'
    kids = 'Kids'


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class Subcategory(Base):
    __tablename__ = 'subcategory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category")
    UniqueConstraint('name', 'category_id', name='uniqNS')


class Brand(Base):
    __tablename__ = 'brand'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class Color(Base):
    __tablename__ = 'color'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(length=7))


class Size(Base):
    __tablename__ = 'size'

    id = Column(Integer, primary_key=True, autoincrement=True)
    size = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category")


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey('brand.id'))
    name = Column(String)
    price = Column(DECIMAL(precision=10, scale=2))
    discount_percent = Column(Integer, default=0)
    quantity = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    sold_quantity = Column(Integer, default=0)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('category.id'))
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'))
    category = Column(Enum(CategoryEnum))


class File(Base):
    __tablename__ = 'file'

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

    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_number = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    ordered_at = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(Enum(StatusEnum))
    payment_method = Column(Enum(PaymentMethodEnum))
    shipping_address_id = Column(Integer, ForeignKey('shipping_address.id'))
    delivery_method_id = Column(Integer, ForeignKey('delivery_method.id'))
    user_card_id = Column(Integer, ForeignKey('user_card.id'), nullable=True)


class ShippingAddress(Base):
    __tablename__ = 'shipping_address'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    shipping_address = Column(Text)


class DeliveryMethod(Base):
    __tablename__ = 'delivery_method'

    id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_company = Column(String)
    delivery_day = Column(String)
    delivery_price = Column(DECIMAL(precision=10, scale=2))


class UserCard(Base):
    __tablename__ = 'user_card'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_number = Column(String)
    card_expiration = Column(String)
    cvc = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))


class Review(Base):
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    star = Column(Integer)
    reviewed_at = Column(TIMESTAMP, default=datetime.utcnow)


class Image(Base):
    __tablename__ = 'image_review'

    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(String)
    review_id = Column(Integer, ForeignKey('review.id'))


class ShoppingCart(Base):
    __tablename__ = 'shopping_cart'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    count = Column(Integer, default=1)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    UniqueConstraint('user_id', 'product_id', name='uniqueSC')


class BankCard(Base):
    __tablename__ = 'bank_card'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_number = Column(String(length=32))
    card_expiration = Column(String(length=4))
    card_cvc = Column(String(length=3), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String, nullable=True)

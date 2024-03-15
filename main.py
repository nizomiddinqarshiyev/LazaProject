from _ast import List
from http.client import HTTPException
from typing import List

from fastapi import FastAPI, APIRouter
from fastapi.params import Depends
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles

from auth.auth import register_router
from market.market import purchasing_system
from payments.payment import payment_root

from auth.utils import verify_token
from database import get_async_session
from market.scheme import ReviewCreate, ReviewGet, LikeScheme, WishlistScheme, WishlistGet
from models.models import Review, Like, Wishlist, Subcategory, Brand, Category, Product, User
from product.product import product_root

router = APIRouter()

app = FastAPI(title='User', version='1.0.0')
app.include_router(payment_root,prefix='/payment')
app.include_router(product_root,prefix='/product')
app.include_router(register_router, prefix='/auth')
app.include_router(purchasing_system, prefix='/purchasing')
# app.mount('/media', StaticFiles(directory='media'), 'files')
app.include_router(register_router, prefix='/auth')


@app.post("/add-review")
async def add_review(
        new_review: ReviewCreate,
        db: Session = Depends(get_async_session),
        token: dict = Depends(verify_token)):
    review = insert(Review).values(
        message=new_review.message,
        user_id=token.get('user_id'),
        product_id=new_review.product_id,
        star=new_review.star)
    await db.execute(review)
    await db.commit()
    return {"success": True, "message": "Review added successfully"}


@app.get('/product/reviews{id}', response_model=List[ReviewGet])
async def get_reviews(
        product_id: int,
        token: dict = Depends(verify_token),
        db: Session = Depends(get_async_session)
):
    async with db as session:
        review_query = select(Review).where(Review.product_id == product_id)
        review_result = await session.execute(review_query)
        reviews = review_result.scalars().all()

        return reviews


@app.post("/products-like")
async def add_like(new_like: LikeScheme, db: Session = Depends(get_async_session), token: dict = Depends(verify_token)):
    try:
        like = insert(Like).values(product_id=new_like.product_id, user_id=token.get('user_id'))
        await db.execute(like)
        await db.commit()
        return {"success": True}
    except IntegrityError:
        raise HTTPException(status_code=404, detail='Invalid data provided')


@app.get("/products/likes")
async def get_likes_for_product(token: dict = Depends(verify_token), db: Session = Depends(get_async_session)):
    async with db as session:
        if token is None:
            raise HTTPException(status_code=403, message="Forbidden")

        query = select(Like.product_id).filter(Like.user_id == token.get('user_id'))
        result = await session.execute(query)
        likes = result.scalars().all()
        products_details = []
        for product_id in likes:
            product = await session.execute(select(Product).where(Product.id == product_id))
            product = product.scalar_one()  # Assuming each product ID will return exactly one product
            subcategory_name = await session.execute(
                select(Subcategory.name).where(Subcategory.id == product.subcategory_id))
            subcategory_name = subcategory_name.scalar_one()
            brand_name = await session.execute(select(Brand.name).where(Brand.id == product.brand_id))
            brand_name = brand_name.scalar_one()
            category_name = await session.execute(select(Category.name).where(Category.id == product.category_id))
            category_name = category_name.scalar_one()

            product_dict = {
                'id': product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "subcategory_name": subcategory_name,
                "quantity": product.quantity,
                "brand_name": brand_name,
                "sold_quantity": product.sold_quantity,
                "category_name": category_name,
                "created_at": product.created_at,
            }
            products_details.append(product_dict)
        return products_details


@app.post('/add-wishlist')
async def add_wishlist(new_wishlist: WishlistScheme, db: Session = Depends(get_async_session), token: dict = Depends(verify_token)):
    try:
        wishlist = insert(Wishlist).values(product_id=new_wishlist.product_id, user_id=token.get('user_id'))
        await db.execute(wishlist)
        await db.commit()
        return {"success": True}
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Invalid data provided")


@app.get('/user/wishlist')
async def get_user_wishlist(token: dict = Depends(verify_token), db: Session = Depends(get_async_session)):
    async with db as session:
        if token is None:
            raise HTTPException(status_code=403, message="Forbidden")
        else:
            wishlist_query = select(Wishlist).where(Wishlist.user_id == token.get('user_id'))
            wishlist_result = await session.execute(wishlist_query)
            wishlist_items = wishlist_result.scalars().all()

            wishlist_details = []
            for wishlist_item in wishlist_items:
                product = await session.execute(select(Product).where(Product.id == wishlist_item.product_id))
                product = product.scalars().one()
                subcategory_name = await session.execute(
                    select(Subcategory.name).where(Subcategory.id == product.subcategory_id)
                )
                subcategory_name = subcategory_name.scalar_one()

                brand_name = await session.execute(select(Brand.name).where(Brand.id == product.brand_id))
                brand_name = brand_name.scalar_one()

                category_name = await session.execute(select(Category.name).where(Category.id == product.category_id))
                category_name = category_name.scalar_one()

                product_dict = {
                    'id': product.id,
                    "name": product.name,
                    "price": product.price,
                    "description": product.description,
                    "subcategory_name": subcategory_name,
                    "brand_name": brand_name,
                    "category_name": category_name,
                    "created_at": product.created_at,
                }
                wishlist_details.append(product_dict)
            return wishlist_details







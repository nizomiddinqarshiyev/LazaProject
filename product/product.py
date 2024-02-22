import datetime
from datetime import datetime
from pathlib import Path

from fastapi import Depends, APIRouter, HTTPException, UploadFile, File
from sqlalchemy.exc import SQLAlchemyError

from auth.utils import verify_token
from database import get_async_session
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import aiofiles
from starlette.responses import FileResponse, JSONResponse

from models.models import Product, Category, Subcategory, Image, Review
from product.schemes import get_product_list, add_product, get_category, add_category, subcategroy_list, Add_subcategory

product_root = APIRouter()


@product_root.get('/product', response_model=List[get_product_list])
async def get_all_products(token: dict = Depends(verify_token),
                           session: AsyncSession = Depends(get_async_session)
                           ):
    if token is not None:
        query = select(Product)
        res = await session.execute(query)
        products = res.scalars().all()
        print(products)
        return products


@product_root.post('/product/delete')
async def delete_product(
        product_id: int,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is not None:
        try:
            res = await session.execute(select(Product).filter(Product.id == product_id))
            if res.scalar():
                query = delete(Product).where(Product.id == product_id)
                await session.execute(query)
                await session.commit()
                return {'success': True, 'message': 'Product deleted'}
            else:
                return {'success': False, 'message': 'Product not found'}
        except SQLAlchemyError as e:
            return {'success': False, 'message': f'Error: {str(e)}'}


@product_root.post('/product/add')
async def add_product(model: add_product,
                      token: dict = Depends(verify_token),
                      session: AsyncSession = Depends(get_async_session)
                      ):
    if token is not None:
        query = insert(Product).values(**dict(model))
        await session.execute(query)
        await session.commit()
        return {'success': True, 'message': "Added successfully!"}


@product_root.get('/categories/', response_model=List[get_category])
async def get_categories(token: dict = Depends(verify_token),
                         session: AsyncSession = Depends(get_async_session)
                         ):
    if token is not None:
        query = select(Category)
        res = await session.execute(query)
        result = res.scalars().all()
        return result


@product_root.post('/categories/add')
async def category_add(model: add_category,
                       token: dict = Depends(verify_token),
                       session: AsyncSession = Depends(get_async_session)
                       ):
    if token is not None:
        query = insert(Category).values(**dict(model))
        await session.execute(query)
        await session.commit()
        return {'success': True, 'message': 'Added successfully!'}


@product_root.get('/subcategory/', response_model=List[subcategroy_list])
async def add_category(token: dict = Depends(verify_token),
                       session: AsyncSession = Depends(get_async_session)
                       ):
    if token is not None:
        query = select(Subcategory)
        res = await session.execute(query)
        result = res.scalars().all()
        return result


@product_root.post('/subcategory/add')
async def add_subcategory(model: Add_subcategory, token: dict = Depends(verify_token),
                          session: AsyncSession = Depends(get_async_session)
                          ):
    if token is not None:
        query = insert(Subcategory).values(**dict(model))
        await session.execute(query)
        await session.commit()
        return {"success": True, "message": "Added Successfully!"}


@product_root.post('/upload-image')
async def add_image(
        product_id: int,
        image: UploadFile = File(...),
        token :dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is not None:
        product = await session.execute(select(Product).filter(Product.id == product_id))
        if not product.scalar():
            return JSONResponse(status_code=404, content={"message": "Product not found"})

        upload_folder = Path("images")
        upload_folder.mkdir(parents=True, exist_ok=True)

        file_path = upload_folder / image.filename
        with file_path.open("wb") as file:
            file.write(await image.read())

        image_url = f"/images/{image.filename}"

        db_image = Image(image=image_url, product=product_id)
        session.add(db_image)
        await session.commit()

        return {"message": "Image uploaded successfully", "image_url": image_url}

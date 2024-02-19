import datetime
from datetime import datetime
from pathlib import Path

from fastapi import Depends, APIRouter, HTTPException, UploadFile, File
from database import get_async_session
from sqlalchemy import select, insert, update,delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import aiofiles
from starlette.responses import FileResponse, JSONResponse

from models.models import Product, Category, Subcategory, Image, Review
from product.schemes import get_product_list, add_product, get_category, add_category, subcategroy_list, Add_subcategory

product_root = APIRouter()

@product_root.get('/product', response_model=List[get_product_list])
async def get_all_products(session: AsyncSession = Depends(get_async_session)):
    query = select(Product)
    res = await session.execute(query)
    products = res.scalars().all()
    print(products)
    return products


@product_root.post('/product/delete')
async def delete_product(
        product_id:int,
        session:AsyncSession=Depends(get_async_session)
):
    if await select(Product).filter(Product.c.id==product_id):
        query = delete(Product).where(Product.c.id==product_id)
        await session.execute(query)
        return {'success':True,'message':'Product deleted'}
    else:
        return {'success':False,'message':'Product not found'}


@product_root.post('/product/add')
async def add_product(model: add_product, session: AsyncSession = Depends(get_async_session)):
    query = insert(Product).values(**dict(model))
    await session.execute(query)
    await session.commit()
    return {'success': True, 'message': "Added successfully!"}


@product_root.get('/categories/', response_model=List[get_category])
async def get_categories(session: AsyncSession = Depends(get_async_session)):
    query = select(Category)
    res = await session.execute(query)
    result = res.scalars().all()
    return result


@product_root.post('/categories/add')
async def category_add(model: add_category, session: AsyncSession = Depends(get_async_session)):
    query = insert(Category).values(**dict(model))
    await session.execute(query)
    await session.commit()
    return {'success': True, 'message': 'Added successfully!'}


@product_root.get('/subcategory/', response_model=List[subcategroy_list])
async def add_category(session: AsyncSession = Depends(get_async_session)):
    query = select(Subcategory)
    res = await session.execute(query)
    result = res.scalars().all()
    return result


@product_root.post('/subcategory/add')
async def add_subcategory(model: Add_subcategory, session: AsyncSession = Depends(get_async_session)):
    query = insert(Subcategory).values(**dict(model))
    await session.execute(query)
    await session.commit()
    return {"success": True, "message": "Added Successfully!"}


@product_root.post('/upload-image')
async def add_image(
        product_id: int,
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session)
):
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




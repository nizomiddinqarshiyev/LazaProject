import datetime
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from _ctypes_test import func
from fastapi import Depends, APIRouter, HTTPException, UploadFile, File
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from fastapi.responses import FileResponse
from auth.utils import verify_token
from database import get_async_session
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import aiofiles

from models.models import Product, Category, Subcategory, Image, Review, Brand, Color, ProductColor, Discount, \
    ProductDiscount
from product.schemes import get_product_list, add_product, get_category, add_category, subcategroy_list, \
    Add_subcategory, Brands, BrandsAdd, Colors, ColorsAdd, ProductColors, Discounts, DiscountsAdd, Product_Discount

product_root = APIRouter()


@product_root.get('/product', response_model=List[get_product_list])
async def get_all_products(token: dict = Depends(verify_token),
                           session: AsyncSession = Depends(get_async_session)
                           ):
    if token is not None:
        query = select(Product)
        res = await session.execute(query)
        products = res.scalars().all()
        # print(products)
        list = []
        for product in products:
            # print(product[1])
            query_brand = select(Brand).where(Brand.id == product.brand_id)
            brand = await session.execute(query_brand)
            brand_detail = brand.first()
            brand_dict = {}
            if brand_detail is not None:
                brand_dict = {
                    'id': brand_detail[0].id,
                    'name': brand_detail[0].name
                }
            query_category = select(Category).where(Category.id == product.category_id)
            category = await session.execute(query_category)
            category_detail = category.first()
            # print(category_detail)
            category_dict = {}
            if category_detail is not None:
                category_dict = {
                    'id': category_detail[0].id,
                    'name': category_detail[0].name
                }
            query_subcategory = select(Subcategory).where(Subcategory.id == product.subcategory_id)
            subcategory = await  session.execute(query_subcategory)
            subcategroy_detail = subcategory.first()
            subcategory_dict = {}
            if subcategroy_detail is not None:
                subcategory_dict = {
                    'id': subcategroy_detail[0].id,
                    'name': subcategroy_detail[0].name,
                    'category_id': subcategroy_detail[0].category_id
                }
            list.append({
                'id': product.id,
                'brand_id': brand_dict,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'created_at': product.created_at,
                'sold_quantity': product.sold_quantity,
                'description': product.description,
                'category_id': category_dict,
                'subcategory_id': subcategory_dict
            })
        await session.commit()
        return list
        print(products)
        return products




@product_root.get('/product/{Product_id}', response_model=List[get_product_list])
async def get_all_products(product_id:int,
                           token: dict = Depends(verify_token),
                           session: AsyncSession = Depends(get_async_session)
                           ):
    if token is not None:
        query = select(Product).where(Product.id==product_id)
        res = await session.execute(query)
        products = res.scalars().all()
        # print(products)
        list = []
        for product in products:
            # print(product[1])
            query_brand = select(Brand).where(Brand.id == product.brand_id)
            brand = await session.execute(query_brand)
            brand_detail = brand.first()
            brand_dict = {}
            if brand_detail is not None:
                brand_dict = {
                    'id': brand_detail[0].id,
                    'name': brand_detail[0].name
                }
            query_category = select(Category).where(Category.id == product.category_id)
            category = await session.execute(query_category)
            category_detail = category.first()
            # print(category_detail)
            category_dict = {}
            if category_detail is not None:
                category_dict = {
                    'id': category_detail[0].id,
                    'name': category_detail[0].name
                }
            query_subcategory = select(Subcategory).where(Subcategory.id == product.subcategory_id)
            subcategory = await  session.execute(query_subcategory)
            subcategroy_detail = subcategory.first()
            subcategory_dict = {}
            if subcategroy_detail is not None:
                subcategory_dict = {
                    'id': subcategroy_detail[0].id,
                    'name': subcategroy_detail[0].name,
                    'category_id': subcategroy_detail[0].category_id
                }
            list.append({
                'id': product.id,
                'brand_id': brand_dict,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'created_at': product.created_at,
                'sold_quantity': product.sold_quantity,
                'description': product.description,
                'category_id': category_dict,
                'subcategory_id': subcategory_dict
            })
        await session.commit()
        return list
        # print(products)
        return products




@product_root.delete('/product/delete')
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
        list_dict = []
        for subcategory in result:
            query_category = select(Category).where(Category.id == subcategory.category_id)
            category = await session.execute(query_category)
            category_detail = category.first()
            category_dict = {}
            if category_detail is not None:
                category_dict = {
                    'id': category_detail[0].id,
                    'name': category_detail[0].name
                }
            list_dict.append({
                'id': subcategory.id,
                'name': subcategory.name,
                'category_id': category_dict
            })
        return list_dict
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
async def product_add(upload_file: UploadFile,
                      product_id : int,
                      token: dict = Depends(verify_token),
                      session: AsyncSession = Depends(get_async_session)):
    if token is not None:
        name = upload_file.filename
        out_file = f'images/{name}'
        async with aiofiles.open(out_file, 'wb') as zipf:
            content = await upload_file.read()
            await zipf.write(content)
        hashcode = secrets.token_hex(32)
        query = insert(Image).values( image=name, hashcode=hashcode,product=product_id)
        await session.execute(query)
        await session.commit()
        return {'success': True, 'message': 'Product added!'}



@product_root.get('/download-image/{hashcode}')
async def download_image(
        hashcode: str,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is not None:
        if hashcode is None:
            raise HTTPException(status_code=404, detail="Invalid hashcode")

        query = select(Image).where(Image.hashcode == hashcode)
        file = await session.execute(query)
        file_data = file.fetchone()

        if file_data is None:
            raise HTTPException(status_code=404, detail="File not found")

        file_url = file_data.url
        file_name = file_data.image
        return FileResponse(path=file_url, media_type='application/octet-stream', filename=file_name)



@product_root.get('/product/brands', response_model=List[Brands])
async def get_brands(token: dict = Depends(verify_token),
                     session: AsyncSession = Depends(get_async_session)
                     ):
    if token is not None:
        query = select(Brand)
        res = await session.execute(query)
        result = res.scalars().all()
        return result
        file_path = upload_folder / image.filename
        with file_path.open("wb") as file:
            file.write(await image.read())

        image_url = f"/images/{image.filename}"


@product_root.post('/product/brands/add')
async def add_brands(model: BrandsAdd,
                     token: dict = Depends(verify_token),
                     session: AsyncSession = Depends(get_async_session)
                     ):
    if token is not None:
        brand_table = Brand.__table__
        query = insert(brand_table).values(**dict(model))
        await session.execute(query)
        await session.commit()
        return {"success": True, "message": "Added successfully"}


@product_root.get('/product/color', response_model=List[Colors])
async def get_colors(token: dict = Depends(verify_token),
                     session: AsyncSession = Depends(get_async_session)
                     ):
    if token is not None:
        query = select(Color)
        res = await session.execute(query)
        result = res.scalars().all()
        return result


@product_root.post('/product/color/add')
async def add_color(model: ColorsAdd,
                    token: dict = Depends(verify_token),
                    session: AsyncSession = Depends(get_async_session)
                    ):
    if token is not None:
        query = insert(Color).values(**dict(model))
        await session.execute(query)
        await session.commit()
        return {"success": True, "message": "Added successfully"}


@product_root.get('/product/Productcolor', response_model=List[ProductColors])
async def get_ProductColor(token: dict = Depends(verify_token),
                           session: AsyncSession = Depends(get_async_session)
                           ):
    if token is not None:
        query = select(ProductColor)
        res = await session.execute(query)
        result = res.scalars().all()
        list_productcolor = []
        for productcolor in result:
            query_productcolor = select(Product).where(Product.id == productcolor.product_id)
            productcolor_query = await session.execute(query_productcolor)
            product_detail = productcolor_query.first()
            productcolor_dict = {}
            if product_detail is not None:
                productcolor_dict = {
                    'id': product_detail[0].id,
                    'brand_id': product_detail[0].brand_id,
                    'name': product_detail[0].name,
                    'price': product_detail[0].price,
                    'quantity': product_detail[0].quantity,
                    'created_at': product_detail[0].created_at,
                    'sold_quantity': product_detail[0].sold_quantity,
                    'description': product_detail[0].description,
                    'category_id': product_detail[0].category_id,
                    'subcategory_id': product_detail[0].subcategory_id
                }
            color_query = select(Color).where(Color.id == productcolor.color_id)
            color_detail = await session.execute(color_query)
            color_result = color_detail.first()
            color_dict = {}
            if color_result is not None:
                color_dict = {
                    'id': color_result[0].id,
                    'code': color_result[0].code
                }
            list_productcolor.append({
                'id': productcolor.id,
                'product_id': productcolor_dict,
                'color_id': color_dict
            })
        await session.commit()
        return list_productcolor


@product_root.post('/product/Prductcolor/add')
async def add_ProductColor(product_id: int,
                           color_id: int,
                           token: dict = Depends(verify_token),
                           session: AsyncSession = Depends(get_async_session)
                           ):
    if token is not None:
        product_query = await session.execute(select(Product).filter(Product.id == product_id))
        if product_query.scalar():
            color_query = await session.execute(select(Color).filter(Color.id == color_id))
            if color_query.scalar():
                query = insert(ProductColor).values(product_id=product_id, color_id=color_id)
                await session.execute(query)
                await session.commit()
                return {"message": "Product color added successfully"}
            else:
                return {"message": "Color not found"}
        else:
            return {"message": "Product not found"}
    else:

        return {"message": "Invalid token"}


@product_root.get('/product/sort_by_brands', response_model=List[get_product_list])
async def get_product_by_brand(brand: int,
                               token: dict = Depends(verify_token),
                               session: AsyncSession = Depends(get_async_session)
                               ):
    if token is not None:
        query = select(Product).where(Product.brand_id == brand)
        res = await session.execute(query)
        products = res.scalars().all()
        # print(products)
        list = []
        for product in products:
            # print(product[1])
            query_brand = select(Brand).where(Brand.id == product.brand_id)
            brand = await session.execute(query_brand)
            brand_detail = brand.first()
            brand_dict = {}
            if brand_detail is not None:
                brand_dict = {
                    'id': brand_detail[0].id,
                    'name': brand_detail[0].name
                }
            query_category = select(Category).where(Category.id == product.category_id)
            category = await session.execute(query_category)
            category_detail = category.first()
            # print(category_detail)
            category_dict = {}
            if category_detail is not None:
                category_dict = {
                    'id': category_detail[0].id,
                    'name': category_detail[0].name
                }
            query_subcategory = select(Subcategory).where(Subcategory.id == product.subcategory_id)
            subcategory = await  session.execute(query_subcategory)
            subcategroy_detail = subcategory.first()
            subcategory_dict = {}
            if subcategroy_detail is not None:
                subcategory_dict = {
                    'id': subcategroy_detail[0].id,
                    'name': subcategroy_detail[0].name,
                    'category_id': subcategroy_detail[0].category_id
                }
            list.append({
                'id': product.id,
                'brand_id': brand_dict,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'created_at': product.created_at,
                'sold_quantity': product.sold_quantity,
                'description': product.description,
                'category_id': category_dict,
                'subcategory_id': subcategory_dict
            })
        await session.commit()
        return list


@product_root.get('/product/sort_by_category', response_model=List[get_product_list])
async def get_product_by_category(category: int,
                                  token: dict = Depends(verify_token),
                                  session: AsyncSession = Depends(get_async_session)
                                  ):
    if token is not None:
        query = select(Product).where(Product.category_id == category)
        res = await session.execute(query)
        products = res.scalars().all()
        # print(products)
        list = []
        for product in products:
            # print(product[1])
            query_brand = select(Brand).where(Brand.id == product.brand_id)
            brand = await session.execute(query_brand)
            brand_detail = brand.first()
            brand_dict = {}
            if brand_detail is not None:
                brand_dict = {
                    'id': brand_detail[0].id,
                    'name': brand_detail[0].name
                }
            query_category = select(Category).where(Category.id == product.category_id)
            category = await session.execute(query_category)
            category_detail = category.first()
            # print(category_detail)
            category_dict = {}
            if category_detail is not None:
                category_dict = {
                    'id': category_detail[0].id,
                    'name': category_detail[0].name
                }
            query_subcategory = select(Subcategory).where(Subcategory.id == product.subcategory_id)
            subcategory = await  session.execute(query_subcategory)
            subcategroy_detail = subcategory.first()
            subcategory_dict = {}
            if subcategroy_detail is not None:
                subcategory_dict = {
                    'id': subcategroy_detail[0].id,
                    'name': subcategroy_detail[0].name,
                    'category_id': subcategroy_detail[0].category_id
                }
            list.append({
                'id': product.id,
                'brand_id': brand_dict,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'created_at': product.created_at,
                'sold_quantity': product.sold_quantity,
                'description': product.description,
                'category_id': category_dict,
                'subcategory_id': subcategory_dict
            })
        await session.commit()
        return list


@product_root.get('/product/sort_by_subcategory', response_model=List[get_product_list])
async def get_product_by_subcategory(subcategory: int,
                                     token: dict = Depends(verify_token),
                                     session: AsyncSession = Depends(get_async_session)
                                     ):
    if token is not None:
        query = select(Product).where(Product.subcategory_id == subcategory)
        res = await session.execute(query)
        products = res.scalars().all()
        # print(products)
        list = []
        for product in products:
            # print(product[1])
            query_brand = select(Brand).where(Brand.id == product.brand_id)
            brand = await session.execute(query_brand)
            brand_detail = brand.first()
            brand_dict = {}
            if brand_detail is not None:
                brand_dict = {
                    'id': brand_detail[0].id,
                    'name': brand_detail[0].name
                }
            query_category = select(Category).where(Category.id == product.category_id)
            category = await session.execute(query_category)
            category_detail = category.first()
            # print(category_detail)
            category_dict = {}
            if category_detail is not None:
                category_dict = {
                    'id': category_detail[0].id,
                    'name': category_detail[0].name
                }
            query_subcategory = select(Subcategory).where(Subcategory.id == product.subcategory_id)
            subcategory = await  session.execute(query_subcategory)
            subcategroy_detail = subcategory.first()
            subcategory_dict = {}
            if subcategroy_detail is not None:
                subcategory_dict = {
                    'id': subcategroy_detail[0].id,
                    'name': subcategroy_detail[0].name,
                    'category_id': subcategroy_detail[0].category_id
                }
            list.append({
                'id': product.id,
                'brand_id': brand_dict,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'created_at': product.created_at,
                'sold_quantity': product.sold_quantity,
                'description': product.description,
                'category_id': category_dict,
                'subcategory_id': subcategory_dict
            })
        await session.commit()
        return list


@product_root.get('/product/sort_by_new_one', response_model=List[get_product_list])
async def get_product_by_New(token: dict = Depends(verify_token),
                             session: AsyncSession = Depends(get_async_session)
                             ):
    if token is not None:
        seven_days = func.now() - timedelta(days=7)
        query = select(Product).where(Product.created_at >= seven_days)
        res = await session.execute(query)
        products = res.scalars().all()
        # print(products)
        list = []
        for product in products:
            # print(product[1])
            query_brand = select(Brand).where(Brand.id == product.brand_id)
            brand = await session.execute(query_brand)
            brand_detail = brand.first()
            brand_dict = {}
            if brand_detail is not None:
                brand_dict = {
                    'id': brand_detail[0].id,
                    'name': brand_detail[0].name
                }
            query_category = select(Category).where(Category.id == product.category_id)
            category = await session.execute(query_category)
            category_detail = category.first()
            # print(category_detail)
            category_dict = {}
            if category_detail is not None:
                category_dict = {
                    'id': category_detail[0].id,
                    'name': category_detail[0].name
                }
            query_subcategory = select(Subcategory).where(Subcategory.id == product.subcategory_id)
            subcategory = await  session.execute(query_subcategory)
            subcategroy_detail = subcategory.first()
            subcategory_dict = {}
            if subcategroy_detail is not None:
                subcategory_dict = {
                    'id': subcategroy_detail[0].id,
                    'name': subcategroy_detail[0].name,
                    'category_id': subcategroy_detail[0].category_id
                }
            list.append({
                'id': product.id,
                'brand_id': brand_dict,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'created_at': product.created_at,
                'sold_quantity': product.sold_quantity,
                'description': product.description,
                'category_id': category_dict,
                'subcategory_id': subcategory_dict
            })
        await session.commit()
        return list
        db_image = Image(image=image_url, product=product_id)
        session.add(db_image)
        await session.commit()

        return {"message": "Image uploaded successfully", "image_url": image_url}


@product_root.get('/product/Discount', response_model=List[Discounts])
async def get_dicounts(token: dict = Depends(verify_token),
                       session: AsyncSession = Depends(get_async_session)
                       ):
    if token is not None:
        query = select(Discount)
        res = await session.execute(query)
        result = res.scalars().all()
        return result


@product_root.post('/product/Discount/Add')
async def get_dicounts(model: DiscountsAdd,
                       token: dict = Depends(verify_token),
                       session: AsyncSession = Depends(get_async_session)
                       ):
    if token is not None:
        query = insert(Discount).values(**dict(model))
        await session.execute(query)
        await session.commit()
        return {"success": True, "message": "Added"}


@product_root.post('/product/DiscountProduct/Add')
async def add_ProductDiscount(product_id: int,
                              discount_id: int,
                              token: dict = Depends(verify_token),
                              session: AsyncSession = Depends(get_async_session)
                              ):
    if token is not None:
        query = select(Product).filter(Product.id == product_id)
        res = await session.execute(query)
        if res.scalar():
            query = select(Discount).filter(Discount.id == discount_id)
            res = await session.execute(query)
            if res.scalar():
                query = insert(ProductDiscount).values(product_id=product_id, discount_id=discount_id)
                await session.execute(query)
                await session.commit()
                return {"success": True, "message": "Added successfully!"}
        else:
            return {"success": False, "message": "Product not found"}


@product_root.get('/product/DiscountProduct', response_model=List[Product_Discount])
async def get_ProductDiscount(token: dict = Depends(verify_token),
                              session: AsyncSession = Depends(get_async_session)
                              ):
    if token is not None:
        query = select(ProductDiscount)
        res = await session.execute(query)
        result = res.scalars().all()
        return result

@product_root.get('/search-product', response_model=List[get_product_list])
async def search_product(
    name : str,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Product).where(Product.name.ilike(f"%{name}%"))
    products = await session.execute(query)
    list = []
    product_data = products.scalars().all()
    if product_data is not None:
        for product in product_data:
            query_brand = select(Brand).where(Brand.id == product.brand_id)
            brand = await session.execute(query_brand)
            brand_detail = brand.first()
            brand_dict = {}
            if brand_detail is not None:
                brand_dict = {
                    'id': brand_detail[0].id,
                    'name': brand_detail[0].name
                }
            query_category = select(Category).where(Category.id == product.category_id)
            category = await session.execute(query_category)
            category_detail = category.first()
            # print(category_detail)
            category_dict = {}
            if category_detail is not None:
                category_dict = {
                    'id': category_detail[0].id,
                    'name': category_detail[0].name
                }
            query_subcategory = select(Subcategory).where(Subcategory.id == product.subcategory_id)
            subcategory = await  session.execute(query_subcategory)
            subcategroy_detail = subcategory.first()
            subcategory_dict = {}
            if subcategroy_detail is not None:
                subcategory_dict = {
                    'id': subcategroy_detail[0].id,
                    'name': subcategroy_detail[0].name,
                    'category_id': subcategroy_detail[0].category_id
                }
            list.append({
                'id': product.id,
                'brand_id': brand_dict,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'created_at': product.created_at,
                'sold_quantity': product.sold_quantity,
                'description': product.description,
                'category_id': category_dict,
                'subcategory_id': subcategory_dict
            })
    else:
        raise NoResultFound('Product not found')
    return list



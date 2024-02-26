from sqlite3 import IntegrityError

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select, update, delete, insert
from sqlalchemy.exc import NoResultFound
from typing import List

from auth.utils import verify_token

from market.scheme import ShoppingCartScheme, ShoppingSaveCartScheme, ShippingAddressScheme, ShippingAddressGetScheme, \
    UserCardScheme, CardScheme, OrderSchema
from market.utils import collect_to_list, step_3
from models.models import ShoppingCart, Product, ShippingAddress, UserCard, Order, ProductOrder, Brand, Category, \
    Subcategory, DeliveryMethod
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session

purchasing_system = APIRouter()


@purchasing_system.post('/shopping-cart')
async def shopping_cart_data(
        data: ShoppingSaveCartScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(ShoppingCart.id).where(
        (ShoppingCart.user_id == token.get('user_id')) & (ShoppingCart.product_id == data.product_id))
    shopping__data = await session.execute(query)
    try:
        shopping_data = shopping__data.one()
        if data.count == 0:
            query3 = delete(ShoppingCart).where(ShoppingCart.id == shopping_data.id)
            await session.execute(query3)
            await session.commit()
            return {'success': True, 'message': 'Product removed'}
        count = shopping_data.count + 1 if data.count is None else data.count
        query3 = update(ShoppingCart).where(ShoppingCart.id == shopping_data.id).values(count=count)
        await session.execute(query3)
        await session.commit()
    except NoResultFound:
        count = 1 if data.count is None else data.count
        query2 = insert(ShoppingCart).values(user_id=token.get('user_id'), product_id=data.product_id, count=count)
        await session.execute(query2)
        await session.commit()
    return {'success': True, 'message': 'Added to shopping cart'}


@purchasing_system.get('/shopping-cart', response_model=List[ShoppingCartScheme])
async def get_shopping_cart(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(ShoppingCart).where(ShoppingCart.user_id == token.get('user_id'))
    shopping_data = await session.execute(query)
    shopping__data = shopping_data.scalars().all()
    print(shopping__data)
    shopping_list = []

    for data in shopping__data:
        products_data = data.product_id
        print(products_data)

        product__detail = select(Product).where(Product.id == products_data)
        execute1 = await session.execute(product__detail)
        execute2 = execute1.scalars().all()

        for product_detail in execute2:
            if product_detail:
                subcategory_name = (await session.execute(
                    select(Subcategory.name).where(Subcategory.id == product_detail.subcategory_id))).scalar()
                brand_name = (await session.execute(select(Brand.name).where(Brand.id == product_detail.brand_id))).scalar()
                category_name = (
                    await session.execute(select(Category.name).where(Category.id == product_detail.category_id))).scalar()

                product_dict = {
                    'id': product_detail.id,
                    "name": product_detail.name,
                    "price": product_detail.price,
                    "description": product_detail.description,
                    "subcategory_name": subcategory_name,
                    "quantity": product_detail.quantity,
                    "brand_name": brand_name,
                    "sold_quantity": product_detail.sold_quantity,
                    "category_name": category_name,
                    "created_at": product_detail.created_at,
                }

                shopping_dict = {
                    'product': product_dict,
                    'id': data.id,
                    'count': data.count,
                    'added_at': data.added_at
                }
                shopping_list.append(shopping_dict)

    return shopping_list


@purchasing_system.post('/shipping-address')
async def post_shipping_address(
        shipping_address_data: ShippingAddressScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(ShippingAddress).where(
        (ShippingAddress.shipping_address == shipping_address_data.shipping_address)).where(
        ShippingAddress.user_id == token.get('user_id'))
    user_exist = await session.execute(query)
    exist = bool(user_exist.scalar())
    if exist is not True:
        query2 = insert(ShippingAddress).values(
            user_id=token.get('user_id'),
            shipping_address=shipping_address_data.shipping_address
        )
        await session.execute(query2)
        await session.commit()
    else:
        raise HTTPException(status_code=400, detail='Shipping address already exists!')
    return {'success': True, 'message': 'Added shipping address'}


@purchasing_system.get('/shipping-address', response_model=ShippingAddressGetScheme)
async def get_user_shipping_addresses(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    try:
        query = select(ShippingAddress).where(ShippingAddress.user_id == token.get('user_id'))
        user_shipping_data = await session.execute(query)
        shipping_address = user_shipping_data.scalar_one_or_none()

        if shipping_address:
            return ShippingAddressGetScheme(
                id=shipping_address.id,
                shipping_address=shipping_address.shipping_address,
                user_id=shipping_address.user_id
            )
        else:
            raise HTTPException(status_code=404, detail="Shipping address not found for the user")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@purchasing_system.post('/add-card')
async def add_card(
        card_detail: UserCardScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    card_number = step_3(card_detail.card_number)
    query = select(UserCard).where(UserCard.card_number == card_number)
    card__data = await session.execute(query)
    card_data = card__data.one_or_none()
    if card_data:
        raise HTTPException(status_code=400, detail='Card already exists!')
    else:
        query2 = insert(UserCard).values(
            card_number=card_number,
            card_expiration=card_detail.card_expiration,
            cvc=card_detail.card_cvc,
            user_id=token.get('user_id')
        )
        await session.execute(query2)
        await session.commit()
    return {'success': True, 'message': 'Successfully added'}


@purchasing_system.get('/user-cards', response_model=List[CardScheme])
async def get_user_cards(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(UserCard.id, UserCard.card_number, UserCard.card_expiration).where(
        UserCard.user_id == token.get('user_id'))
    card__data = await session.execute(query)
    card_data = card__data.all()
    cards_data = collect_to_list(card_data)
    return cards_data


@purchasing_system.post("/orders")
async def create_order(order_data: OrderSchema, token: dict = Depends(verify_token),
                       session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(Order).where(Order.tracking_number == order_data.tracking_number)
    execute1 = await session.execute(query)
    exist = bool(execute1.scalar())

    if exist:
        raise HTTPException(status_code=400, detail='Order already exists!')

    try:
        order = insert(Order).values(
            tracking_number=order_data.tracking_number,
            user_id=token.get('user_id'),
            status=order_data.status,
            payment_method=order_data.payment_method,
            shipping_address_id=order_data.shipping_address_id,
            delivery_method_id=order_data.delivery_method_id,
            user_card_id=order_data.user_card_id
        ).returning(Order.id)
        result = await session.execute(order)
        order_id = result.scalar()
        print('order id', order_id)
        product_order_instance = ProductOrder(
            product_id=order_data.product_id,
            order_id=order_id,
        )
        session.add(product_order_instance)
        await session.commit()
        return {'success': True, 'message': 'Order successfully created'}

    except IntegrityError:
        raise HTTPException(status_code=422, detail="Invalid data provided")


@purchasing_system.get("/orders/")
async def get_order(token: dict = Depends(verify_token), session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(Order.id).where(Order.user_id == token.get('user_id'))
    result = await session.execute(query)
    order_ids = [order[0] for order in result.all()]

    products = []
    count = 0
    for order_id in order_ids:
        count += 1
        query = select(Order).where(Order.id == order_id)
        result = await session.execute(query)
        results1 = result.scalars().all()

        query2 = select(Product).join(ProductOrder).where(ProductOrder.order_id == order_id)
        result2 = await session.execute(query2)
        products_info = result2.scalars().all()

        for info in results1:
            shipping_address_info = (await session.execute(
                select(ShippingAddress.shipping_address).where(
                    ShippingAddress.id == info.shipping_address_id))).scalar()
            user_card_info = (
                await session.execute(select(UserCard.id, UserCard.card_number, UserCard.card_expiration).where(
                    UserCard.id == info.user_card_id))).all()
            delivery_method_info = (
                await session.execute(
                    select(DeliveryMethod).where(DeliveryMethod.id == info.delivery_method_id))).scalar()

        cards_data = collect_to_list(user_card_info)
        products.append({f"{count}. order": {'id': info.id}, "user_id": info.user_id, 'status': info.status,
                         'shipping_address': shipping_address_info, 'user_card': cards_data,
                         'payment_method': info.payment_method,
                         'delivery_method': {'delivery_company': delivery_method_info.delivery_company,
                                             'delivery_day': delivery_method_info.delivery_day,
                                             'delivery_price': delivery_method_info.delivery_price},
                         'ordered_at': info.ordered_at})

        for product in products_info:
            subcategory_name = (await session.execute(
                select(Subcategory.name).where(Subcategory.id == product.subcategory_id))).scalar()
            brand_name = (await session.execute(select(Brand.name).where(Brand.id == product.brand_id))).scalar()
            category_name = (
                await session.execute(select(Category.name).where(Category.id == product.category_id))).scalar()
            print(product.category_id)
            print(category_name)
            datas = ({'id': product.id,
                      "name": product.name,
                      "price": product.price,
                      "description": product.description,
                      "subcategory_name": subcategory_name,
                      "quantity": product.quantity,
                      "brand_name": brand_name,
                      "sold_quantity": product.sold_quantity,
                      "category_name": category_name,
                      "created_at": product.created_at,
                      })
            products.append({
                f'{count}. product': datas})

    return products

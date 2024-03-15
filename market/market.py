from datetime import datetime, timedelta
from sqlite3 import IntegrityError
from decimal import Decimal
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select, update, delete, insert
from sqlalchemy.exc import NoResultFound
from typing import List

from auth.utils import verify_token

from market.scheme import ShoppingCartSchemas, ShoppingSaveCartSchemas, ShippingAddressSchemas, ShippingAddressGetSchemas, \
    UserCardSchemas, CardSchemas, OrderSchemas, ShoppingCountCartSchemas, \
    UserCardDelete, CityAddScheme, CountryScheme, AddressPOSTScheme
from market.utils import collect_to_list, step_3
from models.models import ShoppingCart, Product, ShippingAddress, UserCard, Order, ProductOrder, Brand, Category, \
    Subcategory, DeliveryMethod, Country, City, Address, User
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session

purchasing_system = APIRouter()


@purchasing_system.post('/shopping-cart')
async def shopping_cart_create(
        data: ShoppingSaveCartSchemas,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    query = select(ShoppingCart).where(
        (ShoppingCart.user_id == token.get('user_id')) & (ShoppingCart.product_id == data.product_ids))
    shopping_data = await session.execute(query)
    shopping_cart = shopping_data.scalar_one_or_none()
    if shopping_cart is not None:
        raise HTTPException(status_code=409, detail="This product already exists")
    try:
        shopping_cart_insert = insert(ShoppingCart).values(user_id=token.get('user_id'), product_id=data.product_ids,
                                                           count=1)
        await session.execute(shopping_cart_insert)
        await session.commit()
        return {'success': True, 'message': 'Successfully added to shopping cart'}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@purchasing_system.post('/shopping-cart/count')
async def shopping_cart_count(
        data: ShoppingCountCartSchemas,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(ShoppingCart).where(
        (ShoppingCart.user_id == token.get('user_id')) & (ShoppingCart.product_id == data.product_ids))
    shopping_data = await session.execute(query)
    shopping_cart = shopping_data.scalar_one_or_none()

    if shopping_cart:
        query3 = update(ShoppingCart).where(
            (ShoppingCart.user_id == token.get('user_id')) &
            (ShoppingCart.product_id == data.product_ids)
        ).values(count=data.count)

        await session.execute(query3)
        await session.commit()
        updated_shopping_cart = await session.execute(query)
        updated_shopping_cart = updated_shopping_cart.scalar_one()

        return {"user_id": updated_shopping_cart.user_id, "product_id": updated_shopping_cart.product_id,
                "count": updated_shopping_cart.count}
    else:
        raise HTTPException(status_code=404, detail="Shopping cart not found!")


@purchasing_system.get('/shopping-cart', response_model=List[ShoppingCartSchemas])
async def get_shopping_cart(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    try:
        query = select(ShoppingCart).where(ShoppingCart.user_id == token.get('user_id'))
        shopping_data = await session.execute(query)
        shopping__data = shopping_data.scalars().all()
        shopping_list = []

        delivery = select(DeliveryMethod.delivery_price)
        delivery_data = await session.execute(delivery)
        delivery__data = delivery_data.scalar()
        delivery_price_sync = Decimal(delivery__data)

        for data in shopping__data:
            products_data = data.product_id

            product__detail = select(Product).where(Product.id == products_data)
            execute1 = await session.execute(product__detail)
            execute2 = execute1.scalars().all()

            for product_data in execute2:
                if product_data:
                    subcategory_name = (
                        await session.execute(
                            select(Subcategory.name).where(Subcategory.id == product_data.subcategory_id))
                    ).scalar()
                    brand_name = (
                        await session.execute(select(Brand.name).where(Brand.id == product_data.brand_id))).scalar()
                    category_name = (
                        await session.execute(
                            select(Category.name).where(Category.id == product_data.category_id))).scalar()

                    product_dict = {
                        'id': product_data.id,
                        "name": product_data.name,
                        "price": product_data.price,
                        "description": product_data.description,
                        "subcategory_name": subcategory_name,
                        "quantity": product_data.quantity,
                        "sold_quantity": product_data.sold_quantity,
                        "brand_name": brand_name,
                        "category_name": category_name,
                        "created_at": product_data.created_at,
                    }
                    shopping_dict = {
                        'product': product_dict,
                        'order_id': data.id,
                        'count': data.count,
                        'subtotal': data.count * product_data.price,
                        'shipping_cost': delivery_price_sync,
                        'total': (data.count * product_data.price) + delivery_price_sync,
                        'added_at': data.added_at
                    }
                    shopping_list.append(shopping_dict)

        return shopping_list
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Shopping cart not found")


@purchasing_system.delete('/shopping_cart/delete')
async def purchasing_cart_delete(
        data: ShoppingSaveCartSchemas, token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(ShoppingCart).where(
        (ShoppingCart.user_id == token.get('user_id')) & (ShoppingCart.product_id == data.product_ids))
    delete_query = await session.execute(query)
    exists = bool(delete_query.scalar())
    if exists is True:
        query2 = delete(ShoppingCart).where(
            (ShoppingCart.user_id == token.get('user_id')) & (ShoppingCart.product_id == data.product_ids))
        await session.execute(query2)
        await session.commit()
        return {"message": "Shopping cart has been deleted successfully"}


@purchasing_system.get('/user-cards', response_model=CardSchemas)
async def get_user_cards(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query1 = select(User.last_name).where(User.id == token.get('user_id'))
    user_data = await session.execute(query1)
    user__data = user_data.one()
    users_response = {'user': user__data[0]}
    query2 = select(UserCard.id, UserCard.card_number, UserCard.card_expiration, UserCard.user_id).where(
        UserCard.user_id == token.get('user_id')
    )
    card_data = await session.execute(query2)
    card__data = card_data.all()
    cards_data = collect_to_list(card__data)
    datas = {'user_name': users_response, 'cards': cards_data}
    return datas


@purchasing_system.post('/add-card')
async def add_card(
        card_information: UserCardSchemas,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    try:
        card_number = step_3(card_information.card_numbers)
        query = select(UserCard).where(UserCard.card_number == card_number)
        card_data = await session.execute(query)
        card__data = card_data.one_or_none()
        if card__data:
            raise HTTPException(status_code=400, detail='Card already exists!')
        else:
            insert_card = insert(UserCard).values(
                card_number=card_number,
                card_expiration=card_information.card_expiration,
                cvc=card_information.cvc,
                user_id=token.get('user_id')
            )
            await session.execute(insert_card)
            await session.commit()
            return {'success': True, 'message': 'Cart added successfully!'}, 201
    except KeyError:
        return {"message": "Type proper card information"}


@purchasing_system.delete('/delete-card')
async def delete_card(
        card: UserCardDelete, token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(UserCard).where((UserCard.user_id == token.get('user_id')) & (UserCard.id == card.card))
    query_data = await session.execute(query)
    exist = bool(query_data.scalar())
    if exist is True:
        query = delete(UserCard).where((UserCard.user_id == token.get('user_id')) & (UserCard.id == card.card))
        await session.execute(query)
        await session.commit()
        return {"message": "Card has been deleted successfully"}
    else:
        return {"message": "Card not found"}


@purchasing_system.post("/orders")
async def create_order(
        order_information: OrderSchemas, token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    query = select(Order).where(Order.tracking_number == order_information.tracking_numbers)
    executes = await session.execute(query)
    exists = bool(executes.scalar())
    if exists:
        raise HTTPException(status_code=400, detail='Order already exists!')
    try:
        order_insert = insert(Order).values(
            tracking_number=order_information.tracking_numbers,
            user_id=token.get('user_id'),
            status=order_information.status,
            payment_method=order_information.payment_method,
            shipping_address_id=order_information.shipp_address_id,
            delivery_method_id=order_information.delivery_method_id,
            user_card_id=order_information.user_card_id
        ).returning(Order.id)
        results = await session.execute(order_insert)
        order_id = results.scalar()
        product_order_instance = ProductOrder(
            product_id=order_information.product_ids,
            order_id=order_id,
        )

        session.add(product_order_instance)
        current_day = datetime.now()
        current_day_str = current_day.strftime("%Y-%m-%d")
        future_day = current_day + timedelta(days=7)
        future_day_str = future_day.strftime("%Y-%m-%d")
        formatted_delivery_day = f"{current_day_str}:{future_day_str}"
        query7 = update(DeliveryMethod).values(delivery_day=formatted_delivery_day)
        await session.execute(query7)
        await session.commit()
        return {'success': True, 'message': 'Order successfully created!'}

    except IntegrityError:
        raise HTTPException(status_code=422, detail="Provided invalid data!")


@purchasing_system.get("/orders")
async def get_order(
        token: dict = Depends(verify_token), session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    product_details = []
    query = select(Order.id).where(Order.user_id == token.get('user_id'))
    results = await session.execute(query)
    order_ids = [orders[0] for orders in results.all()]

    counts = 0
    for order_id in order_ids:
        counts += 1
        query = select(Order).where(Order.id == order_id)
        executes = await session.execute(query)
        results1 = executes.scalars().all()

        query2 = select(Product).join(ProductOrder).where(ProductOrder.order_id == order_id)
        result7 = await session.execute(query2)
        products_info = result7.scalars().all()
        for infos in results1:
            shipping_address__info = (await session.execute(
                select(ShippingAddress.shipping_address).where(
                    ShippingAddress.id == infos.shipping_address_id))).scalar()
            user_card__info = (
                await session.execute(select(UserCard.id, UserCard.card_number, UserCard.card_expiration).where(
                    UserCard.id == infos.user_card_id))).all()
            delivery_method__info = (
                await session.execute(
                    select(DeliveryMethod).where(DeliveryMethod.id == infos.delivery_method_id))).scalar()

        cards_data = collect_to_list(user_card__info)
        product_details.append({f"{counts}. order": {'id': infos.id}, "user_id": infos.user_id, 'status': infos.status,
                                'shipping_address': shipping_address__info, 'user_card': cards_data,
                                'payment_method': infos.payment_method,
                                'delivery_method': {'delivery_company': delivery_method__info.delivery_company,
                                                    'delivery_day': delivery_method__info.delivery_day,
                                                    'delivery_price': delivery_method__info.delivery_price},
                                'ordered_at': infos.ordered_at})

        for value in products_info:
            subcategory__name = (await session.execute(
                select(Subcategory.name).where(Subcategory.id == value.subcategory_id))).scalar()
            brand_name = (await session.execute(select(Brand.name).where(Brand.id == value.brand_id))).scalar()
            category__name = (
                await session.execute(select(Category.name).where(Category.id == value.category_id))).scalar()

            datas = ({'id': value.id,
                      "name": value.name,
                      "description": value.description,
                      "price": value.price,
                      "subcategory_name": subcategory__name,
                      "quantity": value.quantity,
                      "brand_name": brand_name,
                      "sold_quantity": value.sold_quantity,
                      "category_name": category__name,
                      "created_at": value.created_at,
                      })
            product_details.append({
                f'{counts}. product': datas})
    return product_details


@purchasing_system.get('/shipping-address', response_model=ShippingAddressGetSchemas)
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
            return ShippingAddressGetSchemas(
                id=shipping_address.id,
                shipping_address=shipping_address.shipping_address,
                user_id=shipping_address.user_id
            )
        else:
            raise HTTPException(status_code=404, detail="Shipping address not found!")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Not found")


@purchasing_system.post('/shipping-address')
async def post_shipping_address(
        shipping_address_data: ShippingAddressSchemas, token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query1 = select(ShippingAddress).where(
        (ShippingAddress.shipping_address == shipping_address_data.shipp_address)).where(
        ShippingAddress.user_id == token.get('user_id'))
    user_exists = await session.execute(query1)
    exists = bool(user_exists.scalar())

    if exists is not True:
        query3 = insert(ShippingAddress).values(
            user_id=token.get('user_id'),
            shipping_address=shipping_address_data.shipp_address
        )
        await session.execute(query3)
        await session.commit()

    else:
        raise HTTPException(status_code=400, detail='Shipping address already exists!')
    return {'success': True, 'message': 'Successfully added shipping address!'}


@purchasing_system.get('/city/{id}')
async def city(
        country_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(City).where(City.country == country_id)
    city__data = await session.execute(query)
    city_data = city__data.scalars().all()
    arr = []
    for city in city_data:
        arr.append({
            'id': city.id,
            'name': city.name
        })
    return arr


@purchasing_system.post('/city-add')
async def create_city(
        city_data: CityAddScheme,
        session: AsyncSession = Depends(get_async_session)
):
    query = insert(City).values(**city_data.dict())
    await session.execute(query)
    await session.commit()
    return {'success': True, 'message': 'City created'}


@purchasing_system.post('/country-add')
async def create_country(
        country_name: str,
        code: str,
        session: AsyncSession = Depends(get_async_session)
):
    query = insert(Country).values(name=country_name, code=code)
    await session.execute(query)
    await session.commit()
    return {'success': True, 'message': 'Country created'}


@purchasing_system.get('/countries', response_model=List[CountryScheme])
async def list_countries(
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Country)
    result = await session.execute(query)
    countries = result.scalars().all()
    return countries


@purchasing_system.post('/add-address')
async def add_address(
        address: AddressPOSTScheme,
        session: AsyncSession = Depends(get_async_session)
):
    query = insert(Address).values(**address.dict())
    data = await session.execute(query)
    print(data)
    return {'success': True, 'message': 'Address successfully saved'}

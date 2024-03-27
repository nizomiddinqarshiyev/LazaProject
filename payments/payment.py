from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update

from payments.scheme import *
from auth.utils import verify_token
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from models.models import BankCard, Invoice, Order
from payments.utils import collect_to_list, step_3


payment_root = APIRouter()


@payment_root.post('/payment/AddCart')
async def add_card(
        card_detail: UserCardScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    card_number = step_3(card_detail.card_number)
    query = select(BankCard).where(BankCard.card_number == card_number)
    card__data = await session.execute(query)
    card_data = card__data.one_or_none()
    if card_data:
        raise HTTPException(status_code=400, detail='Card already exists!')
    else:
        query2 = insert(BankCard).values(
            card_number=card_number,
            card_expiration=card_detail.card_expiration,
            card_cvc=card_detail.card_cvc,
            user_id=token.get('user_id')
        )
        await session.execute(query2)
        await session.commit()
    return {'success': True, 'message': 'Successfully added'}


@payment_root.get('/user-cards', response_model=List[CardScheme])
async def get_user_cards(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    query = select(BankCard).where(BankCard.user_id == token.get('user_id'))
    card__data = await session.execute(query)
    card_data = card__data.all()
    cards_data = collect_to_list(card_data)
    return cards_data


@payment_root.post('/create-invoice')
async def create_invoice(
        invoice_details: CreateInvoiceScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(Order).where(Order.id == int(invoice_details.order_id))
    execute = await session.execute(query)
    check_order = execute.fetchall()

    if not check_order:
        return {'success': False, 'message': 'Order not found'}
    else:
        query = insert(Invoice).values({
            Invoice.amount: invoice_details.amount,
            Invoice.order_id: invoice_details.order_id
        })
        execute = await session.execute(query)
        await session.commit()

        return {'success': True, 'message': 'Invoice created successfully', 'invoice_id': execute.inserted_primary_key[0]}


@payment_root.get('/check-invoice-status')
async def check_invoice_status(
        invoice_id: int,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(Invoice).where(Invoice.id == invoice_id)
    execute = await session.execute(query)
    check_invoice = execute.scalar()

    if not check_invoice:
        return {'success': False, 'message': 'Invoice not found'}
    else:
        return {'status': True, 'invoice_id': invoice_id, 'amount': check_invoice.amount, 'order_id': check_invoice.order_id, 'invoice_status': check_invoice.status}


@payment_root.post('/confirm-invoice')
async def confirm_invoice(
        invoice_id: int,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(Invoice).where(Invoice.id == invoice_id)
    execute = await session.execute(query)
    check_invoice = execute.fetchall()

    if not check_invoice:
        return {'success': False, 'message': 'Invoice not found'}
    else:
        query = update(Invoice).where(Invoice.id == invoice_id).values({
            Invoice.status: 'confirmed'
        })
        await session.execute(query)
        await session.commit()

        return {'status': True, 'message': "Invoice confirmed successfully"}


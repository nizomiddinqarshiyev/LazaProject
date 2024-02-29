from fastapi import APIRouter, Depends
from select import select
from sqlalchemy import select, insert

from .scheme import *
from auth.utils import verify_token
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from models.models import BankCard
from payments.utils import collect_to_list,step_3







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





















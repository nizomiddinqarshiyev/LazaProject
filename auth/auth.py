import jwt
import starlette.status as status
from datetime import datetime
from email.message import EmailMessage
from .scheme import *
from database import get_async_session
# import jwt

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, APIRouter, HTTPException, FastAPI, requests
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from passlib.context import CryptContext
import os
from .utils import verify_token, generate_token, send_mail
from models.models import User

load_dotenv()
register_router = APIRouter()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_SECRET_KEY = os.getenv('GOOGLE_SECRET_KEY')
GOOGLE_REDIRECT_URL = os.getenv('GOOGLE_REDIRECT_URL')


@register_router.post('/register')
async def register(user: UserData, session: AsyncSession = Depends(get_async_session)):
    if user.password1 != user.password2:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    try:
        q_username = select(User).where(User.username == user.username)
        existing_username = await session.execute(q_username)
        if existing_username.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already exists")

        q_email = select(User).where(User.email == user.email)
        existing_email = await session.execute(q_email)
        if existing_email.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already exists")

        password = pwd_context.hash(user.password1)
        user_in_db = UserInDb(**dict(user), password=password, joined_at=datetime.utcnow(), is_verified=True)
        query = insert(User).values(**dict(user_in_db))
        await session.execute(query)
        await session.commit()
        user_info = UserInfo(**dict(user_in_db))
        return dict(user_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@register_router.post('/login')
async def login(user: UserLogin, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(User).where(User.username == user.username)
        userdata = await session.execute(query)
        user_data = userdata.one()

        if user_data[0].email!=user.email:
            return {'success': False, 'message': 'Login failed'}
        if pwd_context.verify(user.password, user_data[0].password):
            token = generate_token(user_data[0].id)
            return token
        else:
            return {'success': False, 'message': 'Login failed'}
    except:
        return {'success': False, 'message': 'Login failed'}


@register_router.get('/user-info', response_model=UserInfo)
async def user_info(token: dict = Depends(verify_token), session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=401, detail='Token not provided!')

    user_id = token.get('user_id')

    query = select(User).where(User.id == user_id)
    user = await session.execute(query)
    try:
        result = user.one()
        user_info = UserInfo(
            first_name=result[0].first_name,
            last_name=result[0].last_name,
            username=result[0].username,
            phone=result[0].phone,
            birth_date=result[0].birth_date
        )
        return user_info
    except NoResultFound:
        raise HTTPException(status_code=404, detail='User not found!')


@register_router.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URL}&scope=openid%20profile%20email&access_type=offline"
    }

@register_router.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, GOOGLE_SECRET_KEY, algorithms=["HS256"])


@register_router.get("/google")
async def auth_google(code: str, session: AsyncSession = Depends(get_async_session)):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_SECRET_KEY,
        "redirect_uri": GOOGLE_REDIRECT_URL,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    user_data = {
        'first_name': user_info.json().get('given_name'),
        'last_name': user_info.json().get('family_name'),
        'username': user_info.json().get('email'),
        'email': user_info.json().get('email'),
        'password': pwd_context.hash(user_info.json().get('email')),
        'image': user_info.json().get('image')
    }
    username = user_data['username']
    email = user_data['email']

    user_exist_query = select(User).where(User.username == user_info.json().get('email'))
    user_exist_data = await session.execute(user_exist_query)
    try:
        result = user_exist_data.scalars().one()
    except NoResultFound:
        try:
            query = insert(User).values(**user_data)
            await session.execute(query)

            user_data = await session.execute(select(User).where(User.username == user_info.json().get('email')))
            user_data = user_data.one()

            token = generate_token(user_data[0].id)
            await session.commit()
            s = f'Your Laza account password >>>>{email} and username >>>> {username}'
            send_mail(email, s)
            return token
        except Exception as e:
            raise HTTPException(detail=f'{e}', status_code=status.HTTP_400_BAD_REQUEST)
    finally:
        await session.close()



from fastapi import Depends, APIRouter, HTTPException, UploadFile
from database import get_async_session
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import aiofiles
from starlette.responses import FileResponse

product_root = APIRouter()


@product_root.get('/product')
async def get_all_products(session: AsyncSession = Depends(get_async_session)):
    query = select()

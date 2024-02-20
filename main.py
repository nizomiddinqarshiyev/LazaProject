from fastapi import FastAPI, APIRouter
from starlette.staticfiles import StaticFiles

from auth.auth import register_router

from product.product import product_root
from auth.auth import register_router
router = APIRouter()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app = FastAPI(title='User', version='1.0.0')
app.include_router(product_root,prefix='/product')
app.include_router(register_router, prefix='/auth')
app.include_router(register_router, prefix='/auth')
app.mount('/media', StaticFiles(directory='media'), 'templates')


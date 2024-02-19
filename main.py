from fastapi import FastAPI

from auth.auth import register_router
from product.product import product_root

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}



app.include_router(product_root)
app.include_router(register_router, prefix='auth')

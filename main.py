import asyncio
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import async_session, engine
from models import Base
from schemas import UserCreate, User, ProductCreate, Product, OrderCreate, Order
import crud

app = FastAPI()

# Create tables at startup (for demonstration)
@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Dependency to get DB session per request
async def get_db():
    async with async_session() as session:
        yield session

@app.post('/products/', response_model=Product)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_product(db, product)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/products/', response_model=List[Product])
async def list_products(skip:int=0, limit:int=100, db: AsyncSession = Depends(get_db)):
    return await crud.list_products(db, skip, limit)

@app.get('/products/{product_id}', response_model=Product)
async def get_product(product_id:int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_product(db, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Product not found')
    return obj

@app.post('/orders/', response_model=Order)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    try:
        o = await crud.create_order(db, order)
        return await crud.get_order(db, o.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/orders/', response_model=List[Order])
async def list_orders(skip:int=0, limit:int=100, db: AsyncSession=Depends(get_db)):
    return await crud.list_orders(db, skip, limit)

@app.get('/orders/{order_id}', response_model=Order)
async def get_order(order_id:int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_order(db, order_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Order not found')
    return obj

@app.post('/orders/{order_id}/complete', response_model=Order)
async def complete_order(order_id:int, db: AsyncSession=Depends(get_db)):
    try:
        o = await crud.complete_order(db, order_id)
        return await crud.get_order(db, o.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Background task for archiving completed orders
async def background_order_archiver():
    # Use a separate session
    while True:
        try:
            async with async_session() as db:
                await crud.archive_old_orders(db, days=30)
            await asyncio.sleep(3600)   # every hour
        except Exception:
            await asyncio.sleep(30)

@app.on_event('startup')
async def start_archiver():
    loop = asyncio.get_event_loop()
    loop.create_task(background_order_archiver())

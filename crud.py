from sqlalchemy.future import select
from sqlalchemy import update, delete, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models import User, Product, Order, OrderItem
from schemas import OrderCreate
from typing import List
import asyncio

async def create_order(db: AsyncSession, order: OrderCreate):
    async with db.begin():
        db_order = Order(user_id=order.user_id, status='open')
        db.add(db_order)
        await db.flush()
        # Lock products for update to avoid race
        product_ids = [item.product_id for item in order.items]
        query = select(Product).where(Product.id.in_(product_ids)).with_for_update()
        result = await db.execute(query)
        products = {prod.id: prod for prod in result.scalars().all()}
        for item in order.items:
            prod = products.get(item.product_id)
            if not prod:
                raise ValueError(f'Product ID {item.product_id} not found')
            if prod.stock < item.quantity:
                raise ValueError(f'Insufficient stock for product {prod.name}')
            prod.stock -= item.quantity
            db_order.items.append(OrderItem(product_id=prod.id, quantity=item.quantity))
        await db.flush()
        await db.refresh(db_order)
    return db_order

async def get_order(db: AsyncSession, order_id: int):
    q = select(Order).options(selectinload(Order.items).selectinload(OrderItem.product)).where(Order.id == order_id)
    r = await db.execute(q)
    return r.scalar_one_or_none()

async def list_orders(db: AsyncSession, skip: int, limit: int):
    q = select(Order).options(selectinload(Order.items).selectinload(OrderItem.product)).order_by(Order.created_at.desc()).offset(skip).limit(limit)
    r = await db.execute(q)
    return r.scalars().all()

async def list_products(db: AsyncSession, skip: int, limit: int):
    q = select(Product).order_by(Product.name).offset(skip).limit(limit)
    r = await db.execute(q)
    return r.scalars().all()

async def get_product(db: AsyncSession, product_id: int):
    q = select(Product).where(Product.id == product_id)
    r = await db.execute(q)
    return r.scalar_one_or_none()

async def create_product(db: AsyncSession, product):
    db_product = Product(**product.dict())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def archive_old_orders(db: AsyncSession, days: int = 30):
    # Archive orders older than `days` days with 'completed' status
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    q = update(Order).where(and_(Order.status == 'completed', Order.created_at < cutoff)).values(status='archived')
    await db.execute(q)
    await db.commit()
    # Optionally: return number of rows updated

async def complete_order(db: AsyncSession, order_id: int):
    async with db.begin():
        q = select(Order).where(Order.id == order_id)
        r = await db.execute(q)
        db_order = r.scalar_one_or_none()
        if not db_order:
            raise ValueError('Order not found')
        if db_order.status != 'open':
            raise ValueError('Order not open')
        db_order.status = 'completed'
        await db.flush()
    await db.refresh(db_order)
    return db_order

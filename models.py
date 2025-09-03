from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func, Index
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    orders = relationship('Order', back_populates='user')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    order_items = relationship('OrderItem', back_populates='product')

Index('ix_products_name', Product.name)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(50), nullable=False, default='open', index=True)
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

Index('ix_orders_status_created_at', Order.status, Order.created_at)

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    order = relationship('Order', back_populates='items', lazy='joined')
    product = relationship('Product', back_populates='order_items', lazy='joined')

Index('ix_order_items_order_product', OrderItem.order_id, OrderItem.product_id, unique=True)

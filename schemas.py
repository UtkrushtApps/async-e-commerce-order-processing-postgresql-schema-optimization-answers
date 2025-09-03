from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    price: float
    stock: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderItem(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: Product

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]

class Order(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: str
    items: List[OrderItem]

    class Config:
        orm_mode = True

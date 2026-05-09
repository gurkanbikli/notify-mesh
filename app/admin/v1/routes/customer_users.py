import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.customer_user import CustomerUser
from app.schemas.customer_user import CustomerUserCreate, CustomerUserResponse, CustomerUserUpdate

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=list[CustomerUserResponse])
async def list_customer_users(db: DB, skip: int = 0, limit: int = 100):
    result = await db.execute(select(CustomerUser).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/", response_model=CustomerUserResponse, status_code=201)
async def create_customer_user(body: CustomerUserCreate, db: DB):
    user = CustomerUser(**body.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{id}", response_model=CustomerUserResponse)
async def get_customer_user(id: uuid.UUID, db: DB):
    user = await db.get(CustomerUser, id)
    if user is None:
        raise HTTPException(status_code=404, detail="Customer user not found")
    return user


@router.patch("/{id}", response_model=CustomerUserResponse)
async def update_customer_user(id: uuid.UUID, body: CustomerUserUpdate, db: DB):
    user = await db.get(CustomerUser, id)
    if user is None:
        raise HTTPException(status_code=404, detail="Customer user not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{id}", status_code=204)
async def delete_customer_user(id: uuid.UUID, db: DB):
    user = await db.get(CustomerUser, id)
    if user is None:
        raise HTTPException(status_code=404, detail="Customer user not found")
    await db.delete(user)
    await db.commit()

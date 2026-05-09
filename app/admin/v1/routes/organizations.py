import re
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug.strip("-")


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(db: DB, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Organization)
        .where(Organization.deleted_at.is_(None))
        .order_by(Organization.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(body: OrganizationCreate, db: DB):
    org = Organization(name=body.name, slug=_slugify(body.name))
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@router.get("/{id}", response_model=OrganizationResponse)
async def get_organization(id: uuid.UUID, db: DB):
    org = await db.get(Organization, id)
    if org is None or org.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.patch("/{id}", response_model=OrganizationResponse)
async def update_organization(id: uuid.UUID, body: OrganizationUpdate, db: DB):
    org = await db.get(Organization, id)
    if org is None or org.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Organization not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(org, key, value)
    await db.commit()
    await db.refresh(org)
    return org


@router.delete("/{id}", status_code=204)
async def delete_organization(id: uuid.UUID, db: DB):
    org = await db.get(Organization, id)
    if org is None or org.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Organization not found")
    org.deleted_at = datetime.now(timezone.utc)
    org.status = "inactive"
    await db.commit()

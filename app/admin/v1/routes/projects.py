import re
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug.strip("-")


@router.get("", response_model=list[ProjectResponse])
async def list_projects(db: DB, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Project)
        .where(Project.deleted_at.is_(None))
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(body: ProjectCreate, db: DB):
    project = Project(
        organization_id=body.organization_id,
        name=body.name,
        slug=_slugify(body.name),
        description=body.description,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{id}", response_model=ProjectResponse)
async def get_project(id: uuid.UUID, db: DB):
    project = await db.get(Project, id)
    if project is None or project.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{id}", response_model=ProjectResponse)
async def update_project(id: uuid.UUID, body: ProjectUpdate, db: DB):
    project = await db.get(Project, id)
    if project is None or project.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{id}", status_code=204)
async def delete_project(id: uuid.UUID, db: DB):
    project = await db.get(Project, id)
    if project is None or project.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Project not found")
    project.deleted_at = datetime.now(timezone.utc)
    project.status = ProjectStatus.inactive
    await db.commit()

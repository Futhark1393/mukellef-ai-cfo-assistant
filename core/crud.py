from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from core import models


def create_tenant(db: Session, name: str, slug: str) -> models.Tenant:
    tenant = models.Tenant(name=name, slug=slug)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def create_user(db: Session, tenant_id, email: str, password_hash: str, role: str) -> models.User:
    user = models.User(tenant_id=tenant_id, email=email, password_hash=password_hash, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.execute(select(models.User).where(models.User.email == email)).scalar_one_or_none()


def get_user_by_id(db: Session, user_id) -> Optional[models.User]:
    return db.execute(select(models.User).where(models.User.id == user_id)).scalar_one_or_none()


def update_refresh_token_hash(db: Session, user: models.User, refresh_token_hash: str) -> models.User:
    user.refresh_token_hash = refresh_token_hash
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_last_login(db: Session, user: models.User) -> models.User:
    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

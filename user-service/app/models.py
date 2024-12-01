from enum import Enum
from app import db
from sqlalchemy import Enum as SQLAlchemyEnum # to avoid conflict with Python's Enum
from sqlalchemy.sql import func
import uuid

class UserRole(Enum):
    DRIVER = "driver"
    RIDER = "rider"

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(SQLAlchemyEnum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

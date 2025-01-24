from . import db
from flask_login import UserMixin
from datetime import datetime,timezone
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    phone_number = db.Column(db.Integer, unique=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    address = db.Column(db.String(150))
    postal_code = db.Column(db.String(150))
    city = db.Column(db.String(150))
    province = db.Column(db.String(150))
    country = db.Column(db.String(150))
    password = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Use timezone-aware datetime
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))  # Update on modification

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    qte_max = db.Column(db.Integer, nullable=False)
    qte_refill = db.Column(db.Integer, nullable=False)
    qte_alert = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String(255), unique=True, nullable=False)
    categories = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_data = db.Column(db.LargeBinary, nullable=True)  # Directly store image binary data
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    


class HST(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # HST_ID
    province = db.Column(db.String(150), unique=True, nullable=False)  # Province
    hst_value = db.Column(db.Float, nullable=False)  # HST_Value

class AuthenticationAdmin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # ID (PK)
    login = db.Column(db.String(150), unique=True, nullable=False)  # Login
    password = db.Column(db.String(150), nullable=False)  # Password
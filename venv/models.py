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
    

class CompanyInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(255), nullable=True)
    
class Billing(db.Model):
    __tablename__ = 'billing'
    Billing_ID = db.Column(db.Integer, primary_key=True)
    Date = db.Column(db.Date, default=datetime.now(timezone.utc))
    Quantity = db.Column(db.Integer, nullable=False)
    Total_BT = db.Column(db.Float, nullable=False)  # Before Tax
    Total_HST = db.Column(db.Float, nullable=False)
    Total_Net = db.Column(db.Float, nullable=False)  # Net Total
    Client_ID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    Observations = db.Column(db.String(255))
    HST_ID = db.Column(db.Integer, db.ForeignKey('hst.id'))
    details = db.relationship('BillDetails', backref='billing', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class BillDetails(db.Model):
    __tablename__ = 'bill_details'
    Bill_Details_ID = db.Column(db.Integer, primary_key=True)
    Billing_ID = db.Column(db.Integer, db.ForeignKey('billing.Billing_ID'), nullable=False)
    Price = db.Column(db.Float, nullable=False)
    Product_ID = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
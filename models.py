from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

# Initialize db
db = SQLAlchemy()

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    photos = relationship("Photo", back_populates="user", lazy=True)
    products = relationship("Product", back_populates="user", lazy=True)

    def __init__(self, email, password):
        self.email = email
        self.password = password

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates="products")

    def __init__(self, name, description, price, qty, user_id):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty
        self.user_id = user_id

# Photo model
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    filename = db.Column(db.String, unique=True, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates="photos")

    def __init__(self, uuid, filename, user_id):
        self.uuid = uuid
        self.filename = filename
        self.user_id = user_id
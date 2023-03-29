from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# Intialise db 
db = SQLAlchemy()

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", backref="products")

    def __init__(self, name, description, price, qty, user_id):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty
        self.user_id = user_id
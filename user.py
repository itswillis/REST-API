''' Create a user model to store user information, including email, password and userID 
    - Modify product model to include a foreign key to the user model, can associate each product and upload photo with specific user
    - Generate a unique identifier for each uploaded photo. 
        - can use hash function such as "", to create a unique hash based on photo's content, filename, and user ID'''


from flask_sqlalchemy import SQLAlchemy
from models import db 

# User model 
class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

    def __init__(self, email, password): 
        self.email = email
        self.password = password

from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from email_validator import validate_email, EmailNotValidError

import os
from dotenv import load_dotenv
load_dotenv()

# Import models from models.py
from models import db, Product

# Import from user.py
from user import User

# Init app 
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite') # look for db.sqlite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY')
print(f"SECRET_KEY: {app.config['SECRET_KEY']}") #print secret key -> can delete soon

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1) # Set to 1-day for testing -> For production delete this due to security purposes
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# Initialise Marshmallow
ma = Marshmallow(app)
# Intialise Bcrypt
bcrypt = Bcrypt(app)

# Initialise db with app 
db.init_app(app)

# Initialise login_manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define the user_loader callback function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables if they do not exist
@app.before_first_request
def create_tables():
    db.create_all()

# Product Schema - Meta class to show
class ProductSchema(ma.Schema): 
    class Meta: 
        fields = ('id', 'name', 'description', 'price', 'qty')

# Initialise Schema
product_schema = ProductSchema() # strict=True
products_schema = ProductSchema(many=True) # strict=True

# Create a Product
@app.route('/product', methods=['POST'])
@jwt_required()
def add_product():
    data = request.get_json()
    name = data['name']
    description = data['description']
    price = data['price']
    qty = data['qty']

    # Check if the product with the same name already exists: 
    existing_product = Product.query.filter_by(name=name).first()
    if existing_product:
        return jsonify({'error': 'Product with the same name already exists.'}), 400

    # Get user_id from the JWT access token 
    user_id = get_jwt_identity()

    new_product = Product(name, description, price, qty, user_id) 

    db.session.add(new_product)
    db.session.commit() # save the database
    
    return product_schema.jsonify(new_product)

# Get all products
@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    user_id = get_jwt_identity()
    all_products = Product.query.filter_by(user_id=user_id).all()
    result = products_schema.dump(all_products)
    return jsonify(result)


# Get single products
@app.route('/product/<id>', methods=['GET'])
@jwt_required()
def get_product(id):
    user_id = get_jwt_identity()
    product = Product.query.filter_by(id=id, user_id=user_id).first()

    if not product:
        return jsonify({'error': 'Product not found or not authorized to access.'}), 404

    return product_schema.jsonify(product)

# Update a product
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    # fetch the product
    product = Product.query.get(id)

    if not product:
        return jsonify({'error': 'Product not found.'}), 404
    
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    product.name = name
    product.description = description 
    product.price = price
    product.qty = qty

    db.session.commit() # save the database
    
    return product_schema.jsonify(product)

# Delete single products
@app.route('/product/<id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = Product.query.get(id)

    # error handling
    if not product:
        return jsonify({'error': 'Product not found.'}), 404
    
    # check if the current user owns the product
    user_id = get_jwt_identity()
    if product.user_id != user_id:
        return jsonify({'error': 'Unauthorized access to product.'}), 403
    
    db.session.delete(product)
    db.session.commit()

    return product_schema.jsonify(product)

# PHOTOS

# Be able to Post photos, retrieve photos, and delete photos NOT DIRECTLY TO DATABASE (as a source URL?)
@app.route('/photos', methods=['POST'])
@jwt_required()
def upload_photo(): 
    user_id = get_jwt_identity() # Replace this with the actual user_id from database

    if 'photo' not in request.files:
        return jsonify({'error': 'No photo uploaded.'}), 400

    photo = request.files['photo']

    if photo.filename == '': 
        return jsonify({'error': 'No photo selected.'}), 400 
    
    if photo and photos.file_allowed(photo, photo.filename): 
        filename = photos.save(photo)
        photo_url = photos.url(filename)
        return jsonify({'photo_url': photo_url, 'user_id': user_id})
    else: 
        return jsonify({'error': 'File not allowed.'}), 400 

# Download/GET photo source
@app.route('/photos/<filename>', methods=['GET'])
@jwt_required()
def download_photo(filename):
    user_id = get_jwt_identity()
    product = Product.query.filter_by(photo_filename=filename).first()

    if not product:
        return jsonify({'error': 'Product not found.'}), 404

    if product.user_id != user_id:
        return jsonify({'error': 'Unauthorized access to photo.'}), 403

    try:
        return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found.'}), 404
    
# Delete a photo
@app.route('/photos/<filename>', methods=['DELETE'])
@jwt_required()
def delete_photo(filename):
    user_id = get_jwt_identity()
    product = Product.query.filter_by(photo_filename=filename).first()

    if not product:
        return jsonify({'error': 'Product not found.'}), 404

    if product.user_id != user_id:
        return jsonify({'error': 'Unauthorized access to photo.'}), 403

    filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'message': 'Photo deleted.'})
    else:
        return jsonify({'error': 'File not found.'}), 404

''' Next steps to handle errors, emails must be valid, passwords can not be empty, emails can not be empty etc.'''
# User registration
@app.route('/register', methods=['POST'])
@app.route('/register', methods=['POST'])
def register_user():
    email = request.json['email']
    password = request.json['password']

    # Validate email
    try:
        validate_email(email)
    except EmailNotValidError as e:
        return jsonify({'error': 'Please enter a valid email.'}), 400

    # Validate password
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long.'}), 400

    # Check if email is already in use
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already in use.'}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(email, hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully.'})

# Initialize JWT with app
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=15))
        return jsonify({
            'access_token': access_token,
            'message': 'Login successful'
        }), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

def user_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'Invalid token.'}), 401

        return fn(user, *args, **kwargs)

    return wrapper

@app.route('/user', methods=['GET'])
@user_required
def get_user_info(user):
    return jsonify({'id': user.id, 'email': user.email})

# Run server
if __name__ ==  '__main__':
    app.run(debug=True)
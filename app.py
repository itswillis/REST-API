from flask import Flask, request, jsonify, send_from_directory, url_for, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_migrate import Migrate
from datetime import timedelta
from functools import wraps
from flask_login import LoginManager # UserMixin, login_user, login_required, logout_user, current_user
from email_validator import validate_email, EmailNotValidError
from hashlib import md5
import uuid
from werkzeug.utils import secure_filename
from flask_jwt_extended.exceptions import JWTDecodeError
import os
from dotenv import load_dotenv
load_dotenv()

# Import models from models.py
from models import db, Product, Photo

# Import from user.py
from models import User

from flask_cors import CORS
# Init app 

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"*": {"origins": "http://127.0.0.1:8080"}})

basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite') # look for db.sqlite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY')
print(f"SECRET_KEY: {app.config['SECRET_KEY']}") #print secret key -> can delete soon

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours = 24) # Set to 1-day for testing -> For production delete this due to security purposes
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# Initialise Marshmallow
ma = Marshmallow(app)
# Intialise Bcrypt
bcrypt = Bcrypt(app)
# Intialise flask_migrate
migrate = Migrate(app, db)

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

    ## ERROR HANDLING
    if existing_product:
        return jsonify({'error': 'Product with the same name already exists.'}), 400
    
    if not name or len(name) > 100: 
        return jsonify({'error': 'Product name should not be empty and must be less than 100 characters.'}), 400 
    
    if not description or len(description) > 500: 
        return jsonify({'error': 'Product description should not be empty and must be less than 500 characters.'}), 400

    if price < 0:
        return jsonify({'error': 'Product price should be a positive number.'}), 400

    if qty < 0 or not isinstance(qty, int):
        return jsonify({'error': 'Product quantity should be a positive integer.'}), 400

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
    product = Product.query.filter_by(id=id, user_id=user_id).first() # Check if it belongs with the user. 

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
    user_id = get_jwt_identity()

    print("Request headers:", request.headers)
    print("Access token:", request.headers.get("Authorization"))

    if 'photo' not in request.files:
        return jsonify({'error': 'No photo uploaded.'}), 400

    photo = request.files['photo']

    if photo.filename == '':
        response = jsonify({'error': f'File not allowed. Filename: {photo.filename}'})
        return response, 422

    unique_id = uuid.uuid4()
    filename = f"{unique_id}_{secure_filename(photo.filename)}"
    user_folder = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    photo_path = os.path.join(user_folder, filename)

    while os.path.exists(photo_path):
        unique_id = uuid.uuid4()
        filename = f"{unique_id}_{secure_filename(photo.filename)}"
        photo_path = os.path.join(user_folder, filename)
    try:
        photo.save(photo_path)
    except Exception as e: 
        response = jsonify({'error': f'Error saving file: {str(e)}'})
        return response, 500

    server_photo_url = url_for('serve_photo', user_id=user_id, filename=filename, _external=True)

    new_photo = Photo(str(unique_id), filename, user_id)

    db.session.add(new_photo)
    db.session.commit()

    response = jsonify({'photo_uuid': str(unique_id), 'user_id': user_id, 'server_photo_url': server_photo_url})
    return response

# Get all photos for a user
@app.route('/photos', methods=['GET'])
@jwt_required()
def get_all_photos():
    user_id = get_jwt_identity()
    user_photos = Photo.query.filter_by(user_id=user_id).all()

    if not user_photos:
        response = jsonify({'error': 'No photos found.'})
        return response, 404

    photos_list = []

    for photo in user_photos:
        photo_url = url_for('serve_photo', user_id=user_id, filename=photo.filename, _external=True)  # Get the URL of the photo
        photo_info = {
            'photo_uuid': photo.uuid,
            'filename': photo.filename,
            'user_id': photo.user_id,
            'photo_url': photo_url  # Include the URL in the response
        }
        photos_list.append(photo_info)

        response = jsonify(photos_list)
        return response

# SERVER PHOTO
@app.route('/photos/<int:user_id>/<filename>', methods=['GET'])
def serve_photo(user_id, filename):
    return send_from_directory(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], str(user_id)), filename)

# Get a specific photo by UUID
@app.route('/photos/uuid/<photo_uuid>', methods=['GET'])
@jwt_required()
def get_photo_by_uuid(photo_uuid):
    user_id = get_jwt_identity()
    photo = Photo.query.filter_by(uuid=photo_uuid).first()

    if not photo:
        return jsonify({'error': 'Photo not found.'}), 404

    if photo.user_id != user_id:
        return jsonify({'error': 'Unauthorized access to photo.'}), 403

    return serve_photo(photo.user_id, photo.filename)  # Use serve_photo function
    
# Delete a photo
@app.route('/photos/uuid/<photo_uuid>', methods=['DELETE'])
@jwt_required()
def delete_photo(photo_uuid):
    user_id = get_jwt_identity()
    photo = Photo.query.filter_by(uuid=photo_uuid).first()

    if not photo:
        return jsonify({'error': 'Photo not found.'}), 404

    if photo.user_id != user_id:
        return jsonify({'error': 'Unauthorized access to photo.'}), 403

    filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], photo.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        db.session.delete(photo)
        db.session.commit()
        return jsonify({'message': 'Photo deleted.'})
    else:
        return jsonify({'error': 'File not found.'}), 404

# User registration
@app.route('/register', methods=['POST'])
def register_user():
    email = request.json['email']
    password = request.json['password']

    if not email: 
        return jsonify({'error': 'Email should not be empty.'}), 400

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

# Add a new error handler to print JWT decode errors
@app.errorhandler(JWTDecodeError)
def handle_jwt_decode_error(e):
    print("JWT decode error:", str(e))
    return jsonify({'msg': 'Not enough segments'}), 422

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

@app.route('/photos', methods=['GET'])
@jwt_required()
def photos_page():
    return render_template('photos.html')

# Run server
if __name__ ==  '__main__':
    app.run(debug=True)
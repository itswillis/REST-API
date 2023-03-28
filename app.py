from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_uploads import UploadSet, configure_uploads, IMAGES


import os
import hashlib

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

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# Intialise db 
db = SQLAlchemy(app)
# Initialise Marshmallow
ma = Marshmallow(app)

# define Products for db.Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True) # should it be nullable=False?
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        # when these are passed in, add to instance
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

# Product Schema - Meta class to show
class ProductSchema(ma.Schema): 
    class Meta: 
        fields = ('id', 'name', 'description', 'price', 'qty')

# Initialise Schema
product_schema = ProductSchema() # strict=True
products_schema = ProductSchema(many=True) # strict=True

# Create a Product
@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    new_product = Product(name, description, price, qty) 

    db.session.add(new_product)
    db.session.commit() # save the database
    
    return product_schema.jsonify(new_product)

# Get all products
@app.route('/product', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)

# Get single products
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    
    # error handling
    if not product:
        return jsonify({'error': 'Product not found.'}), 404
   
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

# Delte single products
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)

    # error handling
    if not product:
        return jsonify({'error': 'Product not found.'}), 404
    
    db.session.delete(product)
    db.session.commit()

    return product_schema.jsonify(product)



# Helper function to generate unique hash for a photo 
def generate_photo_hash(photo, user_id):
    sha256 = hashlib.sha256()
    sha256.update(photo.read())
    sha256.update(str(user_id).encode('utf-8'))
    photo_hash = sha256.hexdigest()
    photo.seek(0)  # Reset file pointer to the beginning
    return photo_hash



#---------------------#
# PHOTOS

# Be able to Post photos, retrieve photos, and delete photos NOT DIRECTLY TO DATABASE (as a source URL?)
@app.route('/photos', methods=['POST'])
def upload_photo(): 
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo uploaded.'}), 400

    photo = request.files['photo']

    if photo.filename == '': 
        return jsonify({'error': 'No photo selected.'}), 400 
    
    if photo and photos.file_allowed(photo, photo.filename): 
        filename = photos.save(photo)
        photo_url = photos.url(filename)
        return jsonify({'photo_url': photo_url})
    else: 
        return jsonify({'error': 'File not allowed.'}), 400 

# Download/GET photo source
@app.route('/photos/<filename>', methods=['GET'])
def download_photo(filename):
    try:
        return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found.'}), 404

# Delete a photo
@app.route('/photos/<filename>', methods=['DELETE'])
def delete_photo(filename):
    filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'message': 'Photo deleted.'})
    else:
        return jsonify({'error': 'File not found.'}), 404


# Run server
if __name__ ==  '__main__':
    app.run(debug=True)
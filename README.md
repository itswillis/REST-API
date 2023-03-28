# REST-API Test Database Server
 - ## Internship Test Project Documentation :sunglasses:

A RESTful API server built using Python, Flask and SQLAlchemy for managing user data.

This project provides a backend software solution for managing user information and data, which is stored in a database. It allows communication with the database through API endpoints, ensuring that users do not have direct access to the database. 

## Features
- Secure and controlled access to the product and user data
- Exposes various API endpoints for managing and retrieving product and user data
- Stores data, including: 
    - USERID
    - PRODUCTS
    - PHOTOS
- Upload, download, and delete product photos

## Getting Started
These instructions will help you set up the project on your local machine for development and testing purposes.

## Prerequisites
- Python 3.x
- Flask
- SQLAlchemy
- Flask-SQLAlchemy
- Flask-Marshmallow
- Flask-Uploads

## Installation
1. Clone the repo 
```bash
git clone https://github.com/itswillis/REST-API.git


2. Create a virtual environment and activate it:

python3 -m venv venv
source venv/bin/activate


3. Install the requred dependencies (this is needed for the app to run):
pip install -r requirements.txt


4. Run the server: 

python3 app.py


The server should be running on 'http://localhost:5000'. 
- Use `Postman` to test



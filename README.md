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
### 1. Clone the repo 
```bash 
git clone https://github.com/itswillis/REST-API.git
```

### 2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the required dependencies (this is needed for the app to run):
```bash
pip3 install -r requirements.txt
```

### 4. Run the server: 
```bash
python3 app.py
```

The server should be running on 'http://localhost:5000'. 
- Use `Postman` to test

### 29/03/23
- [] Handle registration errors (emails can not be empty... etc, throw errors)
- [x] Add a login route that allows users to log in and receive a token for authorisation.
- [x] Add a protected route decorator to restrict access to authorised users.
- [x] Modify the photo upload route to store the user ID with each uploaded photo.
- [] Add a route to get user info by user ID (the user can only see its own information).
- [] Add another column to seperate 'users' and 'admin'. 

#### Authentication Process 
- The user logs in and receives an access_token.
- The client-side application stores the access_token.
- When making requests that require authentication, the client-side application includes the access_token in the Authorisation      header.

#### Potential Bug Fixes
- [] User should be able to 'GET' photos they 'PUT' -> not by their full <filename> but a hash key instead.
- [] Each uploaded photo will be associated with a specific user based on their user_id. Check the 'POST' photos function.
- [] Photos are in another path with 'GET' _uploads/photos/<filename>. 
- [] Photos are not directly linked to the 'products' -> I don't think we want to. 


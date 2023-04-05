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

## Installation :rocket:
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
- [x] Handle registration errors (emails can not be empty... etc, throw errors)
- [x] Add a login route that allows users to log in and receive a token for authorisation.
- [x] Add a protected route decorator to restrict access to authorised users.
- [x] Modify the photo upload route to store the user ID with each uploaded photo.
- [x] Add a route to get user info by user ID (the user can only see its own information).

#### Authentication Process :key:
- The user logs in and receives an access_token.
- The client-side application stores the access_token.
- When making requests that require authentication, the client-side application includes the access_token in the Authorisation      header.

#### PHOTOS Feature :camera_flash:
- `/photos` POST endpoint -> allows users to upload a photo. The photo is saved in the user's folder with a unique UUID as part of the file name. A new 'Photo' object is created and stored in the database with the UUID, filename, and user ID. 
- `/photos` GET endpoint -> retrieves all the photos uploaded by the user. It constructs the photo URL for each photo and includes it in the response. 
- /photos/<int:user_id>/<filename> GET endpoint -> serves a specific photo by user ID and filename. It directly serves the file from the static/images directory.
- /photos/uuid/<photo_uuid> GET endpoint -> retrieves a specific photo by UUID. It queries the photo from the database and uses the serve_photo function to serve the photo.
- /photos/uuid/<photo_uuid> DELETE endpoint: Deletes a specific photo by UUID. It removes the photo from the database and the filesystem.

#### Potential Bug Fixes
- [ ] User should be able to 'GET' photos they 'PUT' -> not by their full <filename> but a hash key instead.
- [ ] Each uploaded photo will be associated with a specific user based on their user_id. Check the 'POST' photos function.
- [ ] Photos are in another path with 'GET' _uploads/photos/<filename>. 
- [ ] Photos are not directly linked to the 'products' -> I don't think we want to. 

### 05/04/23
- [ ] Software architecture

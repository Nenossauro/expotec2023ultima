# Import necessary modules from Flask, pymongo, and os
from flask import Flask, render_template, request, redirect, session, flash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo as mongo
import os

# MongoDB connection URL
url = "mongodb+srv://admin:admin@cluster0.blievi7.mongodb.net/?retryWrites=true&w=majority"

# Create a MongoClient instance with the specified URL and ServerApi version
client = MongoClient(url, server_api=ServerApi('1'))

# Access the 'expotec' database and its collections
db = client["expotec"]
col_users = db["users"]
col_users_info = db["users_info"]

# Define a user object class to represent user data
class user_obj:
    def __init__(self,user,name,email,pwrd,pwrdconf,cnt,stt,cty,hair,shoe):
        self.user = user
        self.name = name
        self.email = email
        self.pwrd = pwrd
        self.pwrdconf = pwrdconf
        self.cnt = cnt
        self.stt = stt
        self.cty = cty
        self.hair = hair        
        self.shoe = shoe

    # Define methods to convert user object to dictionary (JSON) format
    def __dict_user__(self):
        return {
             'email': self.email,
             'user_name': self.user,
             'password': self.pwrd
        }
    def __dict__(self):
        return {
            'name': self.name,
            'cnt': self.cnt,
            'stt': self.stt,
            'cty': self.cty,
            'hair': self.hair,
            'shoe': self.shoe
        }

# Clear console screen for better visualisation
os.system("cls")

# Create a Flask app instance and set a secret key to handle sessions
charts = Flask(__name__)
charts.secret_key = 'enzo'

# Define route to render index.html template
@charts.route('/')
def index():
    return render_template('index.html')

# Define route for registration form submission
@charts.route('/registrar', methods=['POST',])
def regis():
    # Create a new user object with form data
    new_user = user_obj(
        user = request.form['txtusuario'],
        name = request.form['txtnome'],
        email = request.form['txtemail'],
        pwrd = request.form['txtsenha'],
        pwrdconf = request.form['txtsenhaconf'],
        cnt = request.form['txtpais'],
        stt = request.form['txtestado'],
        cty = request.form['txtcidade'],
        hair = request.form['txtcorcabelo'],
        shoe = request.form['txtcalcado']
        )
    # Insert user data as a dictionary (JSON file) into the 'users' collection
    col_users.insert_one(new_user.__dict__())
    
    # Render the index.html template after registration
    return render_template('index.html')

# Run the Flask app
charts.run()

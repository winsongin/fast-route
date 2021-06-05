from flask import Flask, jsonify, request
from dotenv import load_dotenv
from configparser import ConfigParser
import mysql.connector

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

# Reading MySQL credentials from .ini file
config = ConfigParser()
config.read('database.ini')

# Taken from .ini configuration file
HOST = config['mysql']['host']
USER = config['mysql']['user']
PASSWORD = config['mysql']['password']

myDB = mysql.connector.connect( 
    host = HOST, \
    user = USER, \
    password = PASSWORD, \
)

databaseCursor = myDB.cursor() 

# Configure database and tables
databaseCursor.execute('CREATE DATABASE IF NOT EXISTS FastRoute')
databaseCursor.execute('USE FastRoute')
# inventory table will account for salesfloor and backstock
databaseCursor.execute('CREATE TABLE IF NOT EXISTS inventory ( \
    date DATE PRIMARY KEY NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    location VARCHAR(255) NOT NULL, \
    aisle VARCHAR(255) NOT NULL \
)')
# onlineOrders table will account for Ship-From-Store (SFS) and Order Pick-Ups (OPUs)
databaseCursor.execute('CREATE TABLE IF NOT EXISTS onlineOrders ( \
    batch INT PRIMARY KEY NOT NULL, \
    date DATE NOT NULL,\
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    location VARCHAR(255) NOT NULL, \
    aisle VARCHAR(255) NOT NULL, \
    purpose VARCHAR(255) NOT NULL \
)')

# Handle 404 Not Found
@app.errorhandler(404)
def resource_not_found(error): 
    return jsonify(error=str(error)), 404 # Display the error message in the error.html file

@app.route('/home', methods=['GET'])
def home():
    return '<h1>Welcome to the Home page of FastRoute</h1>'

@app.route('/api/v1.0/inventory/salesfloor', methods=['GET','POST'])
def new_inventory(): 
    if request.method == 'GET':
        
        product = request.args.get('product')
        barcode = request.args.get('barcode')

        message = {'product': product, 'barcode': barcode}
        return jsonify(message), 200 # 200 OK status code for successful GET request

    # Handle new barcodes/products
    elif request.method == 'POST':

        parameters = request.get_json(force=True)

        date = parameters['date']
        product = parameters['product']
        barcode = parameters['barcode']
        location = salesfloor
        aisle = parameters['aisle']

        message = {'product': product, 'barcode': barcode, 'location': location}
        return jsonify(message), 201 # 201 OK status code for resource successfully created

# Products can be backstocked if the location on the salesfloor is full
@app.route('/api/v1.0/inventory/backstock', methods=['POST'])
def backstock_product(): 

    parameters = request.get_json(force=True) 
    
    date = parameters['date']
    product = parameters['product'] 
    barcode = parameters['barcode']
    location = "backstock"
    aisle = parameters['aisle']

    message = {'date': date, 'product': product, 'barcode': barcode, 'location': location, 'aisle': aisle}
    return jsonify(message), 201 # 201 OK status code for resource successfully created
    
@app.route('/api/v1.0/inventory/pull', methods=['PUT'])
def pull_product(): 

    parameters = request.get_json(force=True) 

    product = parameters['product']
    barcode = parameters['barcode']
    location = parameters['location']
    date = parameters['date']

# OPUs - Order Pick-Ups
@app.route('/api/v1.0/OPUs')
def picks_for_OPUs():

    parameters = request.get_json(force=True)

    batch = parameters['batch']
    product = parameters['product']
    barcode = parameters['barcode']
    location = parameters['location']
    date = parameters['date'] 
    purpose = "OPUs"

# Pick items for SFS (Ship From Store) batches
@app.route('/api/v1.0/SFS')
def picks_for_SFS():

    parameters = request.get_json(force=True)

    batch = parameters['batch']
    product = parameters['product']
    barcode = parameters['barcode']
    location = parameters['location']
    date = parameters['date']
    purpose = "SFS"


if __name__ == '__main__':
    app.run(debug=True)
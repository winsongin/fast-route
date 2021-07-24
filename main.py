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

# ===================================== MySQL Table Creations =====================================================

# Configure database and tables
databaseCursor.execute('CREATE DATABASE IF NOT EXISTS FastRoute')
databaseCursor.commit()
databaseCursor.execute('USE FastRoute')
databaseCursor.commit()

# Create database table for salesfloor inventory
databaseCursor.execute('CREATE TABLE IF NOT EXISTS salesfloor ( \
    date DATE PRIMARY KEY NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle VARCHAR(255) NOT NULL, \
    quantity INT NOT NULL \
)')
databaseCursor.commit()

# Create database table for backstock inventory
databaseCursor.execute('CREATE TABLE IF NOT EXISTS backstock ( \
    date DATE PRIMARY KEY NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle VARCHAR(255) NOT NULL, \
    quantity INT NOT NULL \
)')
databaseCursor.commit()

# Create database table for Ship From Store (SFS) orders
databaseCursor.execute('CREATE TABLE IF NOT EXISTS orderPickUps ( \
    batch INT PRIMARY KEY NOT NULL, \
    date DATE NOT NULL, \
    fName VARCHAR(255) NOT NULL, \
    lName VARCHAR(255) NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle VARCHAR(255) NOT NULL, \
    quantity INT NOT NULL, \
    status VARCHAR(255) NOT NULL \
)')
databaseCursor.commit()

# Create database table for Order Pick Ups (OPUs) orders
databaseCursor.execute('CREATE TABLE IF NOT EXISTS shipFromStore ( \
    batch INT PRIMARY KEY NOT NULL, \
    date DATE NOT NULL,\
    fName VARCHAR(255) NOT NULL, \
    lName VARCHAR(255) NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle VARCHAR(255) NOT NULL, \
    quantity INT NOT NULL, \
    status VARCHAR(255) NOT NULL \
)')
databaseCursor.commit()

# ==================================== REST API Endpoints/Routes =================================================

# Handle 404 Not Found
@app.errorhandler(404)
def resource_not_found(error): 
    return jsonify(error=str(error)), 404 # Display the error message in the error.html file

@app.route('/home', methods=['GET'])
def home():
    return '<h1>Welcome to the Home page of FastRoute</h1>'

# Retrieve or update inventory information regarding salesfloor
@app.route('/api/v1.0/inventory/salesfloor', methods=['GET','PUT'])
def new_inventory(): 

    # Get the quantity and aisle for a product
    if request.method == 'GET':
        
        product = request.args.get('product')
        barcode = request.args.get('barcode')

        # Retrieve aisle and quantity of a specific product
        query = SELECT (aisle, quantity) FROM salesfloor WHERE product = product AND barcode = barcode
        databaseCursor.execute(query)
        databaseCursor.commit()

        message = {'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
        return jsonify(message), 200

    # Update the quantity in the salesfloor table if someone placed an order
    elif request.method == 'PUT':

        parameters = request.get_json(force=True)

        date = parameters['date']
        product = parameters['product']
        barcode = parameters['barcode']
        aisle = parameters['aisle']
        quantity = parameters['quantity']

        query = "UPDATE salesfloor SET quantity = %s WHERE product = product AND barcode = barcode" 
        values = quantity
        databaseCursor.execute(query, values)
        databaseCursor.commit()

        message = {'date': date, 'product': product, 'barcode': barcode, aisle': aisle, 'quantity': quantity}
        return jsonify(message), 200

# Retrieve or udpate inventory information regarding backstock
@app.route('/api/v1.0/inventory/backstock', methods=['GET','PUT'])
def backstock_product(): 

    # Get the quantity and aisle for a product
    if request.method == 'GET': 

        product = request.args.get('products')
        barcode = request.args.get('barcode')

        # Retrieve aisle and quantity of a specific product
        query = SELECT (aisle, quantity) FROM salesfloor WHERE product = product AND barcode = barcode
        databaseCursor.execute(query) 
        databaseCursor.commit()

        message = {'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
        return jsonify(message), 200

    # Update the quantity in the backstock table if the someone placed an order
    elif request.method == 'PUT':

        parameters = request.get_json(force=True) 
        
        date = parameters['date']
        product = parameters['product'] 
        barcode = parameters['barcode']
        aisle = parameters['aisle']
        quantity = parameters['quantity']


        query = "UPDATE backstock SET quantity = %s WHERE product = product AND barcode = barcode"
        values = quantity 
        databaseCursor.execute(query, values)
        databaseCursor.commit() 
        
        message = {'date': date, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
        return jsonify(message), 200

# Pull inventory from backstock
@app.route('/api/v1.0/inventory/backstock/pull', methods=['PUT'])
def pull_product(): 

    date = request.args.get('date')
    product = request.args.get('product') 
    barcode = request.args.get('barcode')
    location = "salesfloor" # Update location from backstock to salesfloor when the item is pulled from backstock
    aisle = request.args.get('aisle')
    quantity = request.args.get('quantity')


    query = "UPDATE into inventory (date, product, barcode, location, aisle, quantity) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (date, product, barcode, location, aisle, quantity)
    databaseCursor.execute(query, values) 
    databaseCursor.commit() 

    message = {'date': date, 'product': product, 'barcode': barcode, 'location': location, 'aisle': aisle, 'quantity': quantity}
    return jsonify(message), 200

# OPUs - Order Pick-Ups list when customers order online
@app.route('/api/v1.0/fulfillment/OPU', methods=['POST'])
def picks_for_OPUs():

    parameters = request.get_json(force=True)

    batch = request.args.get('batch')
    date = request.args.get('date') 
    fName = request.args.get('fName')
    lName = request.args.get('lName')
    product = request.args.get('product')
    barcode = request.args.get('barcode')
    aisle = request.args.get('aisle')
    quantity = request.args.get('quantity')


    query = "INSERT into orderPickUps (batch, date, fName, lName, product, barcode, aisle, quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (batch, date, fName, lName, product, barcode, aisle, quantity)
    databaseCursor.execute(query, values) 
    databaseCursor.commit()

    message = {'batch': batch, 'date': date, 'fName': fName, 'lName': lName, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
    return jsonify(message), 200

# Pick items for SFS (Ship From Store) batches
@app.route('/api/v1.0/fulfillment/SFS', methods=['POST'])
def picks_for_SFS():

    parameters = request.get_json(force=True)

    batch = request.args.get('batch')
    date = request.args.get('date') 
    fName = request.args.get('fName') 
    lName = request.args.get('lName')
    product = request.args.get('product')
    barcode = request.args.get('barcode')
    aisle = request.args.get('aisle')
    quantity = request.args.get('quantity')


    query = "INSERT into onlineOrders (batch, date, product, barcode, location, aisle, purpose, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (batch, date, fName, lName, product, barcode, aisle, quantity)
    databaseCursor.execute(query, values) 
    databaseCursor.commit()

    message = {'batch': batch, 'date': date, 'fName': fName, 'lName': lName, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
    return jsonify(message), 200

if __name__ == '__main__':
    app.run(debug=True)
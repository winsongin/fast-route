from flask import Flask, jsonify, request
from dotenv import load_dotenv
from datetime import date
from configparser import ConfigParser
from flask_cors import CORS
import mysql.connector

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

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

databaseCursor = myDB.cursor(buffered=True)

# ===================================== MySQL Table Creations =====================================================

# Configure database and tables
databaseCursor.execute('CREATE DATABASE IF NOT EXISTS FastRoute')
myDB.commit()
databaseCursor.execute('USE FastRoute')
myDB.commit()

# Create database table for salesfloor inventory
databaseCursor.execute('CREATE TABLE IF NOT EXISTS salesfloor ( \
    date DATE PRIMARY KEY NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle INT NOT NULL, \
    quantity INT NOT NULL \
)')
myDB.commit()

# Create database table for backstock inventory
databaseCursor.execute('CREATE TABLE IF NOT EXISTS backstock ( \
    date DATE PRIMARY KEY NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle INT NOT NULL, \
    quantity INT NOT NULL \
)')
myDB.commit()

# Create database table for Ship From Store (SFS) orders
databaseCursor.execute('CREATE TABLE IF NOT EXISTS orderPickUps ( \
    date DATE NOT NULL, \
    fName VARCHAR(255) NOT NULL, \
    lName VARCHAR(255) NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle INT NOT NULL, \
    quantity INT NOT NULL, \
    status VARCHAR(255) NOT NULL \
)')
myDB.commit()

# Create database table for Order Pick Ups (OPUs) orders
databaseCursor.execute('CREATE TABLE IF NOT EXISTS shipFromStore ( \
    date DATE NOT NULL,\
    fName VARCHAR(255) NOT NULL, \
    lName VARCHAR(255) NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle INT NOT NULL, \
    quantity INT NOT NULL, \
    status VARCHAR(255) NOT NULL \
)')
myDB.commit()

# ==================================== REST API Endpoints/Routes =================================================

# Handle 404 Not Found
@app.errorhandler(404)
def resource_not_found(error): 
    return jsonify(error=str(error)), 404 # Display the error message in the error.html file

@app.route('/home', methods=['GET'])
def home():
    return '<h1>Welcome to the Home page of FastRoute</h1>'

# Initialize tables that are empty with default values
@app.route('/api/v1.0/inventory/backstock/checkDB', methods=['GET'])
def initializeDB(): 

    if request.method == 'GET': 

            # Check to see if there are existing rows in the table
            query = "SELECT EXISTS(SELECT 1 FROM backstock)"
            if databaseCursor.execute(query) == 0: # 0 means that the table is empty

                message = {'product': 'null', 'barcode': 'null', 'aisle': 'null', 'quantity': 'null'}
                return jsonify(message), 200


    message = {'Message': 'Table has already been initialized'}
    return jsonify(message), 200

# Retrieve or update inventory information regarding salesfloor
@app.route('/api/v1.0/inventory/salesfloor', methods=['GET','PUT'])
def new_inventory(): 

    # Get the quantity and aisle for a product
    if request.method == 'GET':
        
        product = request.args.get('product')
        barcode = request.args.get('barcode')

        # Retrieve aisle and quantity of a specific product
        query = "SELECT (aisle, quantity) FROM salesfloor WHERE product = product AND barcode = barcode"
        databaseCursor.execute(query)
        myDB.commit()

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
        myDB.commit()

        message = {'date': date, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
        return jsonify(message), 200

# Retrieve or udpate inventory information regarding backstock
@app.route('/api/v1.0/inventory/backstock', methods=['GET','PUT'])
def backstock_product(): 

        # Get the quantity and aisle for a product
        if request.method == 'GET': 

            product = request.args.get('products')
            barcode = request.args.get('barcode')

            # Retrieve aisle and quantity of a specific product
            query = "SELECT (aisle, quantity) FROM salesfloor WHERE product = product AND barcode = barcode"
            databaseCursor.execute(query) 
            myDB.commit()

            message = {'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
            return jsonify(message), 200

        # Update the quantity in the backstock table if the someone placed an order
        elif request.method == 'PUT':

            # Check to see if there are existing rows in the table
            # query = SELECT EXISTS(SELECT 1 FROM backstock) 
            # if databaseCursor.execute(query) == 0: # 0 means that the table is empty
                

            
            parameters = request.get_json(force=True) 
            
            date = parameters['date']
            product = parameters['product'] 
            barcode = parameters['barcode']
            aisle = parameters['aisle']
            quantity = parameters['quantity']


            query = "UPDATE backstock SET quantity = %s WHERE product = product AND barcode = barcode"
            values = quantity 
            databaseCursor.execute(query, values)
            myDB.commit() 
            
            message = {'date': date, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
            return jsonify(message), 200

# OPUs - Order Pick-Ups list when customers order online
@app.route('/api/v1.0/fulfillment/OPU', methods=['POST'])
def picks_for_OPUs():

    parameters = request.get_json(force=True)

    date = request.args.get('date') 
    fName = request.args.get('fName')
    lName = request.args.get('lName')
    product = request.args.get('product')
    barcode = request.args.get('barcode')
    aisle = request.args.get('aisle')
    quantity = request.args.get('quantity')


    query = "INSERT into orderPickUps (date, fName, lName, product, barcode, aisle, quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (date, fName, lName, product, barcode, aisle, quantity)
    databaseCursor.execute(query, values) 
    myDB.commit()

    message = {'date': date, 'fName': fName, 'lName': lName, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
    return jsonify(message), 201

# Pick items for SFS (Ship From Store) batches
@app.route('/api/v1.0/fulfillment/SFS', methods=['POST'])
def picks_for_SFS():

    parameters = request.get_json(force=True)

    date = request.args.get('date') 
    fName = request.args.get('fName') 
    lName = request.args.get('lName')
    product = request.args.get('product')
    barcode = request.args.get('barcode')
    aisle = request.args.get('aisle')
    quantity = request.args.get('quantity')


    query = "INSERT into onlineOrders (date, product, barcode, location, aisle, purpose, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (date, fName, lName, product, barcode, aisle, quantity)
    databaseCursor.execute(query, values) 
    myDB.commit()

    message = {'date': date, 'fName': fName, 'lName': lName, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
    return jsonify(message), 201

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, jsonify, request, make_response
from dotenv import load_dotenv
from datetime import date
from configparser import ConfigParser
from flask_cors import CORS, cross_origin
from haversine import haversine, Unit
import mysql.connector

# Global variables initialization
batch = 0 
totalQty = 0
dictLatLong = { 
    'Coca-Cola (6 pack)': (38.590576, -121.489906),
    'Coca-Cola (12 pack)': (34.307144, -106.018066),
    'Double Edge Safety Razor': (45.523064, -122.676483),
    'Electric Shaver': (47.608013, 47.608013),
    'Firestone Walker 805': (33.501324, -111.925278),
    'Elysian Space Dust IPA': (51.049999, -114.066666),
    'Sierra Nevada Hazy IPA': (29.749907, -95.358421),
    'Sour Patch Kids': (43.038902, -87.906471),
    'Tea Tree Shampoo': (42.652580, -73.756233),
    'Tennis Ball - 1 Can (3 Balls)': (41.881832, -87.623177),
    'Tylenol': (32.715736, -117.161087),
    'Advil': (36.114647, -115.172813),
    'Dyson Hair Dryer': (49.246292, -123.116226),
    'Dog Food': (43.651070, -79.347015),
    'Crest 3D White Toothpaste': (42.880230, -78.878738),
    'Basketball': (53.631611, -113.323975),
    'Monopoly Board Game': (47.610378, -122.200676),
    'Tide Detergent': (48.769768, -122.485886)
}

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)
CORS(app, resources={r'/api/v1.0/*': {'origins': 'http://localhost:3000/'}})
# CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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

# # Create database table for salesfloor inventory
# databaseCursor.execute('CREATE TABLE IF NOT EXISTS salesfloor ( \
#     date DATE NOT NULL, \
#     product VARCHAR(255) NOT NULL, \
#     barcode INT NOT NULL, \
#     aisle INT NOT NULL, \
#     quantity INT NOT NULL \
# )')
# myDB.commit()

# Create database table for backstock inventory
databaseCursor.execute('CREATE TABLE IF NOT EXISTS backstock ( \
    date DATE NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle INT NOT NULL, \
    quantity INT NOT NULL \
)')
myDB.commit()

# Create database table for Ship From Store (SFS) orders
databaseCursor.execute('CREATE TABLE IF NOT EXISTS orderPickUps ( \
    batch INT NOT NULL, \
    date DATE NOT NULL, \
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle INT NOT NULL, \
    quantity INT NOT NULL, \
    status VARCHAR(255) NOT NULL, \
    latitude FLOAT(10,6) NOT NULL, \
    longitude FLOAT(10,6) NOT NULL \
)')
myDB.commit()

# Create database table for Order Pick Ups (OPUs) orders
databaseCursor.execute('CREATE TABLE IF NOT EXISTS shipFromStore ( \
    batch INT NOT NULL, \
    date DATE NOT NULL,\
    product VARCHAR(255) NOT NULL, \
    barcode INT NOT NULL, \
    aisle INT NOT NULL, \
    quantity INT NOT NULL, \
    status VARCHAR(255) NOT NULL, \
    latitude FLOAT(10,6) NOT NULL, \
    longitude FLOAT(10,6) NOT NULL \
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
@cross_origin()
def initializeDB(): 

    if request.method == 'GET': 

        print("Checking to see if table exists or not...\n")

        # Check to see if there are existing rows in the table
        query = "SELECT EXISTS(SELECT 1 FROM backstock)"
        databaseCursor.execute(query)
        data = databaseCursor.fetchone()

        if data[0] == 0: # None means that the table is null

            message = {'message': 'Table has not been initialized'}
            return jsonify(message), 200

        message = {'message': 'Table has already been initialized'}
        print(message)
        return jsonify(message), 200

# # Retrieve or update inventory information regarding salesfloor
# @app.route('/api/v1.0/inventory/salesfloor', methods=['GET','PUT'])
# def new_inventory(): 

#     # Get the quantity and aisle for a product
#     if request.method == 'GET':
        
#         product = request.args.get('product')
#         barcode = request.args.get('barcode')

#         # Retrieve aisle and quantity of a specific product
#         query = "SELECT (aisle, quantity) FROM salesfloor WHERE product = product AND barcode = barcode"
#         databaseCursor.execute(query)

#         message = {'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
#         return jsonify(message), 200

#     # Update the quantity in the salesfloor table if someone placed an order
#     elif request.method == 'PUT':

#         parameters = request.get_json(force=True)

#         date = parameters['date']
#         product = parameters['product']
#         barcode = parameters['barcode']
#         aisle = parameters['aisle']
#         quantity = parameters['quantity']

#         query = "UPDATE salesfloor SET quantity = %s WHERE product = product AND barcode = barcode" 
#         values = quantity
#         databaseCursor.execute(query, values)
#         myDB.commit()

#         message = {'date': date, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}
#         return jsonify(message), 200

# Retrieve or udpate inventory information regarding backstock
@app.route('/api/v1.0/inventory/backstock', methods=['GET', 'PUT', 'POST', 'OPTIONS'])
@cross_origin()
def backstock_product(): 

        # Get the quantity and aisle for a product
        if request.method == 'GET': 

            product = request.args.get('product')

            query = "SELECT product, barcode, aisle, quantity FROM backstock WHERE product = %s"
            value = (product,)
            databaseCursor.execute(query, value) 
            result = databaseCursor.fetchone()

            message = {'product': result[0], 'barcode': result[1], 'aisle': result[2], 'quantity': result[3]}
            return jsonify(message), 200

        # Update the quantity in the backstock table
        elif request.method == 'PUT':

            parameters = request.get_json(force=True) 
            
            date = parameters['date']
            product = parameters['product'] 
            barcode = parameters['barcode']
            aisle = parameters['aisle']
            quantity = parameters['quantity']
            
            # Get the current quantity in the backstock inventory so that new quantity can be added to it
            query = "SELECT quantity FROM backstock WHERE date = %s AND product = %s AND barcode = %s AND aisle = %s"
            values = (date, product, barcode, aisle) 
            databaseCursor.execute(query, values)
            currentQuantity = databaseCursor.fetchone()

            newQuantity = quantity + currentQuantity[0] # currentQuantity is a tuple so subscript notation is used to retrieve value at index 0

            query = "UPDATE backstock SET quantity = %s WHERE product = %s AND barcode = %s AND aisle = %s"
            values = (newQuantity, product, barcode, aisle)
            databaseCursor.execute(query, values)
            myDB.commit() 
            
            message = {'date': date, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': newQuantity}
            return jsonify(message), 200

        # Used to initialize the database table if it is currently empty
        elif request.method == 'POST':
            
            parameters = request.get_json()

            date = parameters['date']
            product = parameters['product']
            barcode = parameters['barcode']
            aisle = parameters['aisle']
            quantity = parameters['quantity']

            query = "INSERT INTO backstock (date, product, barcode, aisle, quantity) VALUES (%s, %s, %s, %s, %s)"
            values = (date, product, barcode, aisle, quantity)
            databaseCursor.execute(query, values)
            myDB.commit()

            message = {'date': date, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity}

            return jsonify(message), 200

# OPUs - Order Pick-Ups list when customers order online
@app.route('/api/v1.0/fulfillment/OPU', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def picks_for_OPUs():

    # Global variables initialized at top of file
    global batch
    global totalQty
    global dictLatLong

    if request.method == 'GET': 
        
        query = "SELECT * FROM orderPickUps"
        databaseCursor.execute(query)
        result = databaseCursor.fetchall()
  
        # Create a dictionary with the rows from the MySQL table
        for i in range(len(result)): 
            dictDatabase[i] = result[i]

        biggestBatchNum = (dictDatabase[len(dictDatabase)-1])[0]
        
        for i in range(biggestBatchNum+1): # for-loop that loops through all batch numbers
            start = 0
            for j in range(start, len(dictDatabase)): 
                if i == (dictDatabase[j])[0]: # If i is equal to the batch number of the SQL table row of iteration j
                    tempDict[start] = dictDatabase[j]
                    start = start + 1
        
            newDictDatabase[i] = tempDict
            tempDict = {}
    
        tempDict = {} 
        for i in range(len(newDictDatabase)): # loop through the batches
            for j in range(len(newDictDatabase[i])): 
                for k in range(j, len(newDictDatabase[i])): 
                    if j == k: 
                        tempList.append((k, 0.0))
                    else: 
                        coord1 = (((newDictDatabase[i])[j])[7], ((newDictDatabase[i])[j])[8])
                        coord2 = (((newDictDatabase[i])[k])[7], ((newDictDatabase[i])[k])[8])
                        distance = haversine(coord1, coord2, unit=Unit.MILES) # functon that uses Haversine formula to calculate distance between two (lat, long) coordinate points
                        tempList.append((k, distance))

                tempDict[j] = tempList
                tempList = []

            dictGraph[i] = tempDict
            tempDict = {}
            
        fastestRouteDict = {}
        for i in range(len(dictGraph)):
            visitedVertices = [0] * len(dictGraph[i])
            minWeight = INF
            weight = INF
            vertex = 0 # starting vertex
            minSpanTree = {} 
            edgeCount = 0

            while(edgeCount < len(visitedVertices)): 

                if edgeCount == len(visitedVertices)-1 and minWeight == INF: # If it is the last vertex to be connected to the Min. Span Tree, mark it as visited
                    visitedVertices[minVertex] = True
                    break # break from while-loop to avoid exploring the last vertex as it has already been connected to the Min. Span Tree

                for j in range(len(dictGraph[i])): # Loops through the vertices of each batch 
                    for k in range(1, len((dictGraph[i])[j])): # Loops through each tuple [i.e. (edge, weight) pair]; starts at 1 to avoid 0.0 weight

                        if j == vertex: 
                            
                            tempVertex = (((dictGraph[i])[j])[k])[0]
                            weight = (((dictGraph[i])[j])[k])[1]

                        elif vertex == (((dictGraph[i])[j])[k])[0]: 

                            tempVertex = j
                            weight = (((dictGraph[i])[j])[k])[1]

                        if visitedVertices[tempVertex] == 0 and weight < minWeight: 

                            minWeight = weight 
                            minVertex = tempVertex

                visitedVertices[vertex] = True # Mark the vertex as visited     

                minSpanTree[vertex] = (minVertex, minWeight) # Add to minSpanTree aka the dictionary that holds the route
                edgeCount = edgeCount + 1 # Update edgeCount to ensure that the number of edges is n-1; n being the number of vertices
                vertex = minVertex # Set the next vertex to the current minVertex as that will be explored next
                minWeight = INF # Reset minWeight for next while-loop iteration
                # Reset weight and tempVertex to prevent inaccuracy in calculations by using weight and tempVertex from last while-loop's iteration
                weight = INF 
                tempVertex = minVertex

            fastestRouteDict[i] = minSpanTree # Assign batch i in fastestRouteDict to its corresponding Min. Span Tree
        
        # for i in range(len(fastestRouteDict)):
        #     print("fastestRouteDict[batch][{}]: {}".format(i, fastestRouteDict[i]))

        fastestRouteBatches = {}
        tempDict = {}
        # Replace all the vertices with the corresponding table entry from MySQL database
        for i in range(len(fastestRouteDict)): 
            y = 0 # starting vertex of every iteration
            for j in range(len(fastestRouteDict[i])+1): 
                tempDict[j] = (newDictDatabase[i])[y]
                if j != len(fastestRouteDict[i]): # If it is not the last (edge, weight) tuple to be explored in batch i's dictionary, set y to the edge from that tuple
                    y = ((fastestRouteDict[i])[y])[0]

            fastestRouteBatches[i] = tempDict
            tempDict = {}

        # for i in range(len(fastestRouteBatches)): 
        #     print("fastestRouteBatches[{}]: ".format(i))
        #     for j in range(len(fastestRouteBatches[i])): 
        #         print("\t{}: {}".format(j, (fastestRouteBatches[i])[j]))

        return jsonify(fastestRouteDict), 200

    elif request.method == 'POST':

        if totalQty >= 15: # If the total quantity for the batch has reached 15, start a new batch
        
            batch += 1
            totalQty = 0

        parameters = request.get_json(force=True)

        date = parameters['date']
        # fName = parameters['fName']
        # lName = parameters['lName']
        product = parameters['product']
        barcode = parameters['barcode']
        aisle = parameters['aisle']
        quantity = parameters['quantity']
        status = parameters['status']
        latitude = float(dictLatLong[product][0])
        longitude = float(dictLatLong[product][1])

        totalQty += int(quantity)

        query = "INSERT into orderPickUps (batch, date, product, barcode, aisle, quantity, status, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (batch, date, product, barcode, aisle, quantity, status, latitude, longitude)
        databaseCursor.execute(query, values)
        myDB.commit()
        

        message = {'date': date, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity, 'status': status, 'latitude': latitude, 'longitude': longitude}
        return jsonify(message), 201

# Pick items for SFS (Ship From Store) batches
@app.route('/api/v1.0/fulfillment/SFS', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def picks_for_SFS():

    # Global variables initialized at top of file
    global batch
    global totalQty
    global dictLatLong

    # Local variables
    dictDatabase = {} # Stores all of the rows from the database table
    newDictDatabase = {} # Stores all of the rows from the database table based on batches
    tempDict = {} # Used to temporarily store all vertices for each batch
    dictGraph = {} # Adjacency list that represents a graph's edges and respective weights
    tempList = [] # Temporary list to store tuples that represent edges and weights (i.e. (vertex, weight))
    INF = 999999

    if request.method == 'GET': 

        query = "SELECT * FROM shipFromStore"
        databaseCursor.execute(query)
        result = databaseCursor.fetchall()
  
        # Create a dictionary with the rows from the MySQL table
        for i in range(len(result)): 
            dictDatabase[i] = result[i]

        biggestBatchNum = (dictDatabase[len(dictDatabase)-1])[0]
        
        for i in range(biggestBatchNum+1): # for-loop that loops through all batch numbers
            start = 0
            for j in range(start, len(dictDatabase)): 
                if i == (dictDatabase[j])[0]: # If i is equal to the batch number of the SQL table row of iteration j
                    tempDict[start] = dictDatabase[j]
                    start = start + 1
        
            newDictDatabase[i] = tempDict
            tempDict = {}
    
        tempDict = {} 
        for i in range(len(newDictDatabase)): # loop through the batches
            for j in range(len(newDictDatabase[i])): 
                for k in range(j, len(newDictDatabase[i])): 
                    if j == k: 
                        tempList.append((k, 0.0))
                    else: 
                        coord1 = (((newDictDatabase[i])[j])[7], ((newDictDatabase[i])[j])[8])
                        coord2 = (((newDictDatabase[i])[k])[7], ((newDictDatabase[i])[k])[8])
                        distance = haversine(coord1, coord2, unit=Unit.MILES) # functon that uses Haversine formula to calculate distance between two (lat, long) coordinate points
                        tempList.append((k, distance))

                tempDict[j] = tempList
                tempList = []

            dictGraph[i] = tempDict
            tempDict = {}
            
        fastestRouteDict = {}
        for i in range(len(dictGraph)):
            visitedVertices = [0] * len(dictGraph[i])
            minWeight = INF
            weight = INF
            vertex = 0 # starting vertex
            minSpanTree = {} 
            edgeCount = 0

            while(edgeCount < len(visitedVertices)): 

                if edgeCount == len(visitedVertices)-1 and minWeight == INF: # If it is the last vertex to be connected to the Min. Span Tree, mark it as visited
                    visitedVertices[minVertex] = True
                    break # break from while-loop to avoid exploring the last vertex as it has already been connected to the Min. Span Tree

                for j in range(len(dictGraph[i])): # Loops through the vertices of each batch 
                    for k in range(1, len((dictGraph[i])[j])): # Loops through each tuple [i.e. (edge, weight) pair]; starts at 1 to avoid 0.0 weight

                        if j == vertex: 
                            
                            tempVertex = (((dictGraph[i])[j])[k])[0]
                            weight = (((dictGraph[i])[j])[k])[1]

                        elif vertex == (((dictGraph[i])[j])[k])[0]: 

                            tempVertex = j
                            weight = (((dictGraph[i])[j])[k])[1]

                        if visitedVertices[tempVertex] == 0 and weight < minWeight: 

                            minWeight = weight 
                            minVertex = tempVertex

                visitedVertices[vertex] = True # Mark the vertex as visited     

                minSpanTree[vertex] = (minVertex, minWeight) # Add to minSpanTree aka the dictionary that holds the route
                edgeCount = edgeCount + 1 # Update edgeCount to ensure that the number of edges is n-1; n being the number of vertices
                vertex = minVertex # Set the next vertex to the current minVertex as that will be explored next
                minWeight = INF # Reset minWeight for next while-loop iteration
                # Reset weight and tempVertex to prevent inaccuracy in calculations by using weight and tempVertex from last while-loop's iteration
                weight = INF 
                tempVertex = minVertex

            fastestRouteDict[i] = minSpanTree # Assign batch i in fastestRouteDict to its corresponding Min. Span Tree
        
        # for i in range(len(fastestRouteDict)):
        #     print("fastestRouteDict[batch][{}]: {}".format(i, fastestRouteDict[i]))

        fastestRouteBatches = {}
        tempDict = {}
        # Replace all the vertices with the corresponding table entry from MySQL database
        for i in range(len(fastestRouteDict)): 
            y = 0 # starting vertex of every iteration
            for j in range(len(fastestRouteDict[i])+1): 
                tempDict[j] = (newDictDatabase[i])[y]
                if j != len(fastestRouteDict[i]): # If it is not the last (edge, weight) tuple to be explored in batch i's dictionary, set y to the edge from that tuple
                    y = ((fastestRouteDict[i])[y])[0]

            fastestRouteBatches[i] = tempDict
            tempDict = {}

        for i in range(len(fastestRouteBatches)): 
            print("fastestRouteBatches[{}]: ".format(i))
            for j in range(len(fastestRouteBatches[i])): 
                print("\t{}: {}".format(j, (fastestRouteBatches[i])[j]))

        return jsonify(fastestRouteBatches), 200


    elif request.method == 'POST':

        if totalQty >= 15: # If the total quantity for the batch has reached 15, start a new batch

            batch += 1
            totalQty = 0

        parameters = request.get_json(force=True)

        date = parameters['date']
        # fName = parameters['fName']
        # lName = parameters['lName']
        product = parameters['product']
        barcode = parameters['barcode']
        aisle = parameters['aisle']
        quantity = parameters['quantity']
        status = parameters['status']
        latitude = float(dictLatLong[product][0])
        print("Latitude: {}\n".format(latitude))
        longitude = float(dictLatLong[product][1])
        print("Longitude: {}\n".format(longitude))

        totalQty += int(quantity)

        query = "INSERT into shipFromStore (batch, date, product, barcode, aisle, quantity, status, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (batch, date, product, barcode, aisle, quantity, status, latitude, longitude)
        databaseCursor.execute(query, values)
        myDB.commit()

        message = {'date': date, 'product': product, 'barcode': barcode, 'aisle': aisle, 'quantity': quantity, 'status': status, 'latitude': latitude, 'longitude': longitude}
        return jsonify(message), 201

if __name__ == '__main__':
    app.run(debug=True)
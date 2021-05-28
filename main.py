from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

# Handle 404 Not Found
@app.errorhandler(404)
def resource_not_found(error): 
    return jsonify(error=str(error)), 404 # Display the error message in the error.html file

@app.route('/home', methods=['GET'])
def home():
    return '<h1>Welcome to the Home page of FastRoute</h1>'

@app.route('/api/v1.0/inventory/salesfloor', methods=['GET','POST'])
def new_inventory(): 

    # Handle new barcodes/products
    if request.methods == 'POST': 
        parameters = request.get_json(force=True)

        product = parameters['product']
        barcode = parameters['barcode']
        location = parameters['location']
        date = parameters['date']

        message = {'product': product, 'barcode': barcode, 'location': location}
        return jsonify(message), 201 # 201 OK status code for resource successfully created

# Products can be backstocked if the location on the salesfloor is full
@app.route('/api/v1.0/inventory/backstock', methods=['POST'])
def backstock_product(): 

    parameters = request.get_json(force=True) 
    
    product = parameters['product'] 
    barcodeNum = parameters['barcode']
    date = parameters['date']

    # Need to somehow determine backstock locations
    
# @app.route('api/v1.0/inventory/pull', methods=['PUT'])
# def pull_product(): 
#     pass

if __name__ == '__main__':
    app.run(debug=True)
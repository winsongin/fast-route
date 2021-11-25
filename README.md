# Fast Route

## Prerequisites

- Python 3.8.0
- Flask (2.0.1)
  - **pip3 install flask**
- Python-dotenv (0.17.1)
  - **pip3 install python-dotenv**
- MySQL Connector Python (8.0.25)
  - **pip3 install mysql-connector-python**
- Flask-CORS
  - **pip3 install -U flask-cors**
- Haversine

  - Haversine Formula:
    - Calculates the distance between two points that are in (longitude, latitude) coordinate pairs
  - Longitude and latitude must be in decimal degrees
  - **pip3 install haversine**

- Nginx (Reverse Proxy/HTTP Server)

  - On MacOS:
    - Ensure that Homebrew is installed
    - Run the following commands to install Nginx:
      - brew install update
      - brew install nginx
    - To start Nginx:
      - nginx
    - To stop Nginx:
      - nginx -s stop

- Gunicorn
  - Gunicorn is the WSGI application server for the Flask application
  - To install Gunicorn, run the following command:
    - pip install gunicorn

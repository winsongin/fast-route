# Fast Route

## Prerequisites

- Python 3.8.0
- Flask (2.0.1)
  - **pip3 install flask**
- Python-dotenv (0.17.1)
  - **pip3 install python-dotenv**
- MySQL Connector Python (8.0.25)
  - **pip3 install mysql-connector-python**
- Flask-CORS (3.0.10)
  - **pip3 install -U flask-cors**
- Haversine (2.5.1)

  - Haversine Formula:
    - Calculates the distance between two points that are in (latitude, longitude) coordinate pairs
  - Longitude and latitude must be in decimal degrees
  - **pip3 install haversine**

- Gunicorn (20.1.0)

  - Gunicorn is the WSGI application server for the Flask application
  - To install Gunicorn, run the following command:
    - pip install gunicorn

- Additional Files Needed:
  - .env
    Enter the following:
    - FLASK_APP=main.py
    - FLASK_ENV=development
  - database.ini
    - Contents in the format below:
      - **Note:** Enter the following information that corresponds to your MySQL configuration
        [mysql]
        host =
        user =
        password =

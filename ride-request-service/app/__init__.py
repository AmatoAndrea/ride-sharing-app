from flask import Flask
from flask_pymongo import PyMongo
from app.routes import ride_bp
from app.config import Config
from app.logger import setup_logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize logging
    setup_logging(app)

    # Initialize PyMongo
    mongo = PyMongo(app)
    app.mongo = mongo

    # Register blueprints
    app.register_blueprint(ride_bp)

    return app
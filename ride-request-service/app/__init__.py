import json

from flask import Flask
from flask_pymongo import PyMongo
from kafka import KafkaProducer

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

    # Initialize Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=app.config['KAFKA_BOOTSTRAP_SERVERS'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    app.kafka_producer = producer

    # Register blueprints
    app.register_blueprint(ride_bp)

    return app
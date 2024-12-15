import json
from threading import Thread

from flask import Flask
from kafka import KafkaConsumer
import redis

from app.config import Config
from app.logger import setup_logging
from app.routes import driver_bp
from app.consumer import consume_ride_requests

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Setup logging
    setup_logging(app)

    # Initialize the Redis client
    app.redis_client = redis.Redis(host=app.config['REDIS_HOST'])

    # Initialize Kafka Consumer
    consumer = KafkaConsumer(
        app.config['KAFKA_TOPIC'],
        bootstrap_servers=app.config['KAFKA_BOOTSTRAP_SERVERS'],
        group_id=app.config['KAFKA_GROUP_ID'],
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    app.consumer = consumer

    # Start the kafka consumer in a separate thread
    consumer_thread = Thread(target=consume_ride_requests, args=(app,))
    consumer_thread.daemon = True
    consumer_thread.start()


    # Register blueprints
    app.register_blueprint(driver_bp)

    return app

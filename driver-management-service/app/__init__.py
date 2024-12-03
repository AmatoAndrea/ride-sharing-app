from flask import Flask
import redis
from app.config import Config
from app.logger import setup_logging
from app.routes import driver_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Setup logging
    setup_logging(app)

    # Initialize the Redis client
    app.redis_client = redis.Redis(host=app.config['REDIS_HOST'])

    # Register blueprints
    app.register_blueprint(driver_bp)

    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from app.logger import setup_logging

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize logging
    setup_logging(app)
    
    # Initialize database
    db.init_app(app)

    from app.routes import user_bp
    app.register_blueprint(user_bp)

    with app.app_context():
        db.create_all()

    return app

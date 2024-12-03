from dotenv import load_dotenv
import os

class Config:
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))


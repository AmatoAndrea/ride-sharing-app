from dotenv import load_dotenv
import os

class Config:
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
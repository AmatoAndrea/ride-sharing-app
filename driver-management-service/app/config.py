#from dotenv import load_dotenv
import os

class Config:
    #load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'ride_requests')
    KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'driver-management-service-group')
    RIDE_REQUEST_SERVICE_URL = os.getenv('RIDE_REQUEST_SERVICE_URL', 'http://ride-request-service:5001')

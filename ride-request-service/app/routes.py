from flask import Blueprint, request, jsonify, current_app, g
import uuid
from datetime import datetime, timezone
from enum import Enum
from app.utils import token_required

ride_bp = Blueprint('ride_bp', __name__)

# Define ride status
class RideStatus(Enum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

@ride_bp.route('/rides/request', methods=['POST'])
@token_required
def create_ride_request():
    data = request.get_json()
    user_id = g.get('user_id')
    username = data.get('username')
    pickup_location = data.get('pickup_location')
    dropoff_location = data.get('dropoff_location')

    current_app.logger.info(f"Ride request for user: {user_id}")

    # Validate input
    if not all([user_id, username, pickup_location, dropoff_location]):
        current_app.logger.warning("Missing required fields during ride request")
        return jsonify({'message': 'Missing required fields'}), 400

    # Create new ride request
    request_id = str(uuid.uuid4())
    ride_request = {
        'request_id': request_id,
        'user_id': user_id,
        'username': username,
        'pickup_location': pickup_location,
        'dropoff_location': dropoff_location,
        'status': RideStatus.PENDING.value,
        'created_at': datetime.now(timezone.utc)
    }

    # Save ride request to MongoDB
    current_app.mongo.db.ride_requests.insert_one(ride_request)

    current_app.logger.info(f"Ride request created successfully: {request_id}")
    return jsonify({'request_id': request_id, 'status': RideStatus.PENDING.value}), 201

@ride_bp.route('/rides/status/<request_id>', methods=['GET'])
# @token_required
def get_ride_status(request_id):
    # user_id = g.get('user_id')
    current_app.logger.info(f"Fetching ride status by ID: {request_id}")
    # current_app.logger.info(f"Fetching ride status by ID: {request_id} by user: {user_id}")
    ride_request = current_app.mongo.db.ride_requests.find_one({'request_id': request_id})
    # ride_request = current_app.mongo.db.ride_requests.find_one({'request_id': request_id, 'user_id': user_id})
    if ride_request:
        current_app.logger.info(f"Ride status: {ride_request['status']}")
        return jsonify({'status': ride_request['status']}), 200
    else:
        current_app.logger.warning("Ride request not found")
        # current_app.logger.warning("Ride request not found or user not authorized")
        return jsonify({'message': 'Ride request not found'}), 404
        # return jsonify({'message': 'Ride request not found or user not authorized'}), 404
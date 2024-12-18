from flask import Blueprint, request, jsonify, current_app, g
import uuid
from datetime import datetime, timezone
from enum import Enum
import requests
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

    # Retrieve username from user-service
    user_service_url = current_app.config.get('USER_SERVICE_URL')
    try:
        response = requests.get(f"{user_service_url}/users/id/{user_id}", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error contacting user-service: {e}")
        return jsonify({'message': 'Failed to verify user information'}), 503

    user_data = response.json()
    user_service_username = user_data.get('username')
    user_service_role = user_data.get('role')

    if not user_service_username or user_service_username != username:
        current_app.logger.warning("Username mismatch during ride request")
        return jsonify({'message': 'Username does not match user ID'}), 400

    if not user_service_role or user_service_role != 'rider':
        current_app.logger.warning("User is not authorized to request rides")
        return jsonify({'message': 'User is not authorized to request rides'}), 403

    # Create new ride request
    request_id = str(uuid.uuid4())
    ride_request = {
        'request_id': request_id,
        'user_id': user_id,
        'username': username,
        'pickup_location': pickup_location,
        'dropoff_location': dropoff_location,
        'status': RideStatus.PENDING.value,
        'created_at': datetime.now(timezone.utc).isoformat()
    }

    # Save ride request to MongoDB
    current_app.mongo.db.ride_requests.insert_one(ride_request)

    # Remove '_id' field added by MongoDB
    ride_request.pop('_id', None)

    # Send ride request to Kafka
    current_app.kafka_producer.send(current_app.config['KAFKA_TOPIC'], ride_request)
    current_app.kafka_producer.flush()

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

@ride_bp.route('/rides/update_status', methods=['PUT'])
# @token_required
def update_ride_status():
    data = request.get_json()
    request_id = data.get('request_id')
    new_status = data.get('status')
    # Validate input
    if not all([request_id, new_status]):
        return jsonify({'message': 'Missing required fields'}), 400
    # Update ride status in MongoDB
    result = current_app.mongo.db.ride_requests.update_one(
        {'request_id': request_id},
        {'$set': {'status': new_status}}
    )
    if result.matched_count:
        current_app.logger.info(f"Ride status updated to {new_status} for request_id: {request_id}")
        return jsonify({'message': 'Ride status updated successfully'}), 200
    else:
        current_app.logger.warning("Ride request not found")
        return jsonify({'message': 'Ride request not found'}), 404
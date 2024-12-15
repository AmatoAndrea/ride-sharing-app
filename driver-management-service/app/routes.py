from flask import Blueprint, request, jsonify, current_app
import json

driver_bp = Blueprint('driver', __name__)

@driver_bp.route('/drivers/update_status', methods=['POST'])
def update_driver_status():
    data = request.get_json()
    driver_id = data.get('driver_id')
    status = data.get('status')

    current_app.logger.info(f"Updating driver status for driver: {driver_id}")

    # Validate input
    if not all([driver_id, status]):
        current_app.logger.warning("Missing required parameters during driver status update")
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Update driver status
    if status == 'AVAILABLE':
        current_app.redis_client.sadd('drivers:available', driver_id)
        current_app.logger.info(f"Driver {driver_id} set to AVAILABLE")
    else:
        current_app.redis_client.srem('drivers:available', driver_id)
        current_app.logger.info(f"Driver {driver_id} set to UNAVAILABLE")

    return jsonify({'message': 'Driver status updated'}), 200

@driver_bp.route('/drivers/assigned_rides/<driver_id>', methods=['GET'])
def get_assigned_rides(driver_id):
    current_app.logger.info(f"Fetching assigned rides for driver: {driver_id}")

    try:
        assigned_rides_key = f"driver:{driver_id}:assigned_rides"
        rides = current_app.redis_client.lrange(assigned_rides_key, 0, -1)
        rides = [json.loads(ride.decode('utf-8')) for ride in rides]

        current_app.logger.info(f"Assigned rides: {rides}")
        return jsonify({'assigned_rides': rides}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching assigned rides: {e}")
        return jsonify({'error': 'Unable to fetch assigned rides'}), 500
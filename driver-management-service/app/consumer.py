from datetime import datetime
import json
from enum import Enum
# import requests

from app.utils import find_available_driver


class RideStatus(Enum):
    """
    Enum representing the status of a ride.
    """
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'


def consume_ride_requests(app):
    """
    Consumes ride requests from the application's consumer, assigns available drivers,
    updates ride statuses, and manages related data storage.

    Args:
        app: The Flask application instance containing the consumer, logger, and Redis client.

    Functionality:
        - Processes incoming ride request messages.
        - Finds and assigns available drivers to ride requests.
        - Updates the ride status to 'ACCEPTED' and records the assignment time.
        - Stores assigned rides in Redis.
        - Logs assignments and handles cases with no available drivers.
    """
    with app.app_context():
        for message in app.consumer:
            ride_request = message.value
            app.logger.info(f"Received ride request: {ride_request}")

            # Attempt to assign the ride to a driver
            driver_id = find_available_driver(app.redis_client)
            if driver_id:
                ride_request['driver_id'] = driver_id
                ride_request['status'] = RideStatus.ACCEPTED.value
                ride_request['assigned_at'] = datetime.utcnow().isoformat()

                # Store assigned ride
                assigned_rides_key = f"driver:{driver_id}:assigned_rides"
                app.redis_client.rpush(assigned_rides_key, json.dumps(ride_request))
                app.logger.info(f"Assigned ride {ride_request['request_id']} to driver: {driver_id}")

                # # Update ride status in ride-request-service
                # ride_request_service_url = app.config.get('RIDE_REQUEST_SERVICE_URL')
                # try:
                #     response = requests.put(
                #         f"{ride_request_service_url}/rides/update_status",
                #         json={
                #             'request_id': ride_request['request_id'],
                #             'status': RideStatus.ACCEPTED.value
                #         },
                #         timeout=5
                #     )
                #     response.raise_for_status()
                #     app.logger.info(f"Ride status updated to ACCEPTED for request_id: {ride_request['request_id']}")
                # except requests.exceptions.RequestException as e:
                #     app.logger.error(f"Failed to update ride status: {e}")
                #     # Revert driver's status to AVAILABLE
                #     app.redis_client.sadd('available_drivers', driver_id)
                #     app.logger.info(f"Driver {driver_id} status reverted to AVAILABLE")
                #     # Handle failure to update ride status
                #     continue

                # TODO: Implement the SAGA pattern by updating the ride status in the ride-request-service
                # Potential steps to implement:
                # 1. Send a request to the ride-request-service to update the ride status to 'ACCEPTED'.
                # 2. Ensure the ride-request-service updates the status successfully.
                # 3. If the ride-request-service fails to update the status, revert the driver status to 'AVAILABLE'.
                # 4. Implement compensating actions if the ride assignment fails at any step.
                # ...
            else:
                app.logger.warning("No available drivers for ride request")
                # TODO: No available drivers; implement a compensating action (SAGA):
                # Possible actions:
                # 1. Notifying the ride-request-service to update the ride status to 'FAILED' or 'PENDING'.
                # 2. Sending a notification to the user informing them that no drivers are available.
                # 3. Implementing a retry mechanism to attempt to find a driver again after a certain period.
                # 4. Updating the ride status back to 'pending' or 'failed' in the ride-request-service DB.
                # ...
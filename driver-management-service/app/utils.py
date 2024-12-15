import redis

# TODO: Change the implementation of this function in order to find the best
# available driver based on the driver's current location and the ride's pickup
def find_available_driver(redis_client):
    """
    Find and return an available driver from the Redis set "drivers:available".

    This function pops a driver ID from the Redis set "drivers:available" and returns it.
    If no driver ID is available, it returns None.

    Args:
        redis_client (Redis): An instance of a Redis client.

    Returns:
        str or None: The ID of an available driver as a string, or None if no driver is available.
    """

    driver_id = redis_client.spop("drivers:available")
    if driver_id is not None:
        return driver_id.decode('utf-8')
    return None


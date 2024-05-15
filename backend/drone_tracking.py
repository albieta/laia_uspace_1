from shapely.geometry import Point, LineString
from datetime import datetime
from laiagenlib.Domain.Shared.Utils.logger import _logger

def verify_coordinates(coordinates: list, timestamp: str, flight_plan: dict):
    
    drone_timestamp = datetime.fromisoformat(timestamp)

    departure_time = datetime.fromisoformat(flight_plan["departure_time"])
    arrival_time = datetime.fromisoformat(flight_plan["arrival_time"])
    route = flight_plan["route"]['geometry']['coordinates']

    if not (departure_time <= drone_timestamp <= arrival_time):
        return False

    flight_path = LineString(route)
    drone_point = Point(coordinates)

    nearest_point = flight_path.interpolate(flight_path.project(drone_point))

    return nearest_point.distance(drone_point) < 0.01
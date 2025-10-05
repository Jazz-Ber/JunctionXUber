# self.py
import geopy.distance
import math
from TypeChooser import get_venue_type
from Services.CSVService import Id_To_Name

class Controller:
    def __init__(self, client):
        self.busy_address = (52.07515870380299, 4.3082185994332525)
        self.idle_address = (51.85096345959651, 4.543824271176097)
        self.client = client


    def getLocations(self, current_coords):
        """
        Retrieve nearby locations based on the current coordinates and currently open venue types.

        This method determines which venue categories are open at the current time using the
        `get_venue_type()` function, then queries the Foursquare API for locations of those types
        within a 10 km radius of the provided coordinates.

        Args:
            current_coords (tuple): A tuple of (latitude, longitude) representing the current location.

        Returns:
            list: A list of (latitude, longitude) tuples for each location found by the API.

        Notes:
            - The method uses the FoursquareClient instance (`self.client`) to make the API request.
            - Only locations with valid latitude and longitude are included in the result.
            - The search is limited to 50 results and a 10,000 meter radius.
            - Venue types are determined dynamically based on current time and day.
        """
        types = ""
        venue_types = get_venue_type()
        if venue_types and venue_types[0] != "No venues open at this time":
            types = ",".join(venue_types)

        params = {
            "ll": f"{current_coords[0]},{current_coords[1]}",
            "radius": 10000,
            "limit": 50,
            "open_now": True,
            "fsq_category_ids": types
        }

        response = self.client.getNearbyLocations(params)
        result = response.json().get("results", [])
        result_coords = []

        for i in result:
            lat = i.get("latitude", None)
            long = i.get("longitude", None)

            if not lat or not long:
                continue

            result_coords.append((lat, long))

        return result_coords

    # Methods to update addresses
    def set_busy_address(self, addr):
        self.busy_address = addr

    def set_idle_address(self, addr):
        self.idle_address = addr

    # Methods to get addresses
    def get_busy_address(self, clusters, current_coords):
        if not clusters:
            return None
        
        scores = []
        for i in clusters:
            scores.append((len(i[0]) / math.sqrt(round(geopy.distance.geodesic(current_coords, i[1]).km, 3))))

        return clusters[scores.index(max(scores))][1]


    def get_idle_address(self, clusters, current_coords):
        if not clusters:
            return None
        
        scores = []
        for i in clusters:
            scores.append((len(i[0]) / math.sqrt(round(geopy.distance.geodesic(current_coords, i[1]).km, 3))))

        busy_location =  clusters[scores.index(max(scores))][1]

        p = {
            "ll": f"{busy_location[0]},{busy_location[1]}",
            "radius": 1000,
            "limit": 10,
            "open_now": True,
            "fsq_category_ids": "4c38df4de52ce0d596b336e1",
            "sort": "DISTANCE"
        }

        response = self.client.getNearbyLocations(p)
        result = response.json().get("results", [])
        result_coords = []

        for i in result:

            lat = i.get("latitude", None)
            long = i.get("longitude", None)

            if not lat or not long:
                continue

            result_coords.append((lat, long))

        if not result_coords:
            return None

        return result_coords[0]
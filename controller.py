import geopy.distance
import math
from TypeChooser import get_venue_type

class Controller:
    def __init__(self, client):
        self.busy_address = (52.07515870380299, 4.3082185994332525)
        self.idle_address = (51.85096345959651, 4.543824271176097)
        self.client = client


    def getLocations(self, current_coords):
        """
        Gets all the close locations to go to at the given time
        """
        types = ""
        venue_types = get_venue_type()
        if venue_types and venue_types[0] != "No venues open at this time":
            types = ",".join(venue_types)

        print(types)

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

    def set_busy_address(self, addr):
        self.busy_address = addr

    def set_idle_address(self, addr):
        self.idle_address = addr

    def get_busy_address(self, clusters, current_coords):
        """
        Finds the optimal spot for new requests
        """
        if not clusters:
            return self.busy_address
        
        scores = []
        for i in clusters:
            scores.append((len(i[0]) / math.sqrt(round(geopy.distance.geodesic(current_coords, i[1]).km, 3))))

        return clusters[scores.index(max(scores))][1]


    def get_idle_address(self, clusters, current_coords):
        """
        Finds a parking lot in the neighbourhood for some down time
        """
        if not clusters:
            return self.idle_address
        
        scores = []
        for i in clusters:
            scores.append((len(i[0]) / math.sqrt(round(geopy.distance.geodesic(current_coords, i[1]).km, 3))))

        busy_location =  clusters[scores.index(max(scores))][1]

        print(busy_location)

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
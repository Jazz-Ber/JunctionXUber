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
        types = ""
        for i in get_venue_type():
            types += i
            types += ","
        types = types.rstrip(types[-1])

        params = {
            "ll": f"{round(current_coords[0], 4)},{round(current_coords[1], 4)}",
            "radius": 10000,
            "limit": 50,
            "open_now": True,
            "categories": types
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
            return self.busy_address
        
        scores = []
        for i in clusters:
            scores.append((len(i[0]) / math.sqrt(round(geopy.distance.geodesic(current_coords, i[1]).km, 3))))

        return clusters[scores.index(max(scores))][1]


    def get_idle_address(self, clusters):
        return self.idle_address
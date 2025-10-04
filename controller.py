# self.py
import geopy.distance
import math
from TypeChooser import get_venue_type
from Services.CSVService import Id_To_Name

class Controller:
    def __init__(self, client):
        self.busy_address = "Den Haag"
        self.idle_address = "Barendrecht"
        self.client = client


    def getLocations(self, current_coords):
        types = ""
        for i in get_venue_type():
            types += i
            types += ","
        types = types.rstrip(types[-1])

        params = {
            "ll": f"{round(current_coords[0], 4)},{round(current_coords[1], 4)}",  # lat,lng # Should be coordinates that map is currently on.
            "radius": 10000,
            "limit": 50,
            "categories": types
        }

        response = self.client.getNearbyLocations(params)
        result = response.json().get("results", [])
        result_addresses = []

        for i in result:
            distance = i.get("distance", None)
            if not distance:
                continue

            location_data = i.get("location", None)
            if not location_data:
                continue

            address = location_data.get("address", None)
            postcode = location_data.get("postcode", None)
            city = location_data.get("locality", None)
            if not address or not postcode or not city:
                continue

            result_addresses.append(f"{address}, {postcode} {city}")
            #idle_location = result[1].get("location", {})
            #self.set_idle_address(idle_location.get("formatted_address", self.get_idle_address(None)))

        # Print for debugging
        #print("Idle:", self.get_idle_address(None))
        return result_addresses

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

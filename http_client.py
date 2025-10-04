import requests

class FoursquareClient:
    def __init__(self, key):
        self.key = key
        self.url = "https://places-api.foursquare.com/places/search"
        self.headers = {
            "Authorization": "Bearer "+key,
            "X-Places-Api-Version": "2025-06-17",
            "Accept": "application/json"
        }
        
    def getNearbyLocations(self, params=None):
        response = requests.get(self.url, headers=self.headers, params=params)
        return response
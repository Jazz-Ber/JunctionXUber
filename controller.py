# The main controller script

from ui import App
import tkinter as tk
from http_client import FoursquareClient
from config_loader import ConfigLoader

config = ConfigLoader("configs/config.json")
#print(config)
fourSquareAPIKey = config.get_key()
#print(fourSquareAPIKey)
client = FoursquareClient(fourSquareAPIKey)

# Test for parameters
params = {
    "ll": "51.9986,4.3718",  # latitude,longitude
    "radius": 200,              # This is in meters
    "limit": 2,
    #"categories": "13065"       # Example: coffee shops, you can add multiple
}
response = client.getNearbyLocations(params)
#print(response.status_code)
print(response.json())

app = App()
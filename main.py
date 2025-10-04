# main.py
import tkinter as tk
from controller import Controller
from http_client import FoursquareClient
from config_loader import ConfigLoader
from ui import App

# Load config & API key
config = ConfigLoader("configs/config.json")
fourSquareAPIKey = config.get_key()
client = FoursquareClient(fourSquareAPIKey)

# Prepare controller
controller = Controller()

# Make API request
params = {
    "ll": "51.9986,4.3718",  # lat,lng
    "radius": 200,
    "limit": 2
}

response = client.getNearbyLocations(params)
result = response.json().get("results", [])
print(result)
print(len(result))

# Update controller addresses from API result
if len(result) > 1:
    busy_location = result[0].get("location", {})
    idle_location = result[1].get("location", {})

    controller.set_busy_address(busy_location.get("formatted_address", controller.get_busy_address()))
    controller.set_idle_address(idle_location.get("formatted_address", controller.get_idle_address()))

# Print for debugging
print("Busy:", controller.get_busy_address())
print("Idle:", controller.get_idle_address())

# Pass the same controller to the UI
app = App(controller)
app.start()

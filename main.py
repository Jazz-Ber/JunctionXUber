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
controller = Controller(client)
app = App(controller)

# Pass the same controller to the UI
app.start()

import tkinter as tk
from controller import Controller
from http_client import FoursquareClient
from config_loader import ConfigLoader
from ui import App

config = ConfigLoader("configs/config.json")
fourSquareAPIKey = config.get_key()
client = FoursquareClient(fourSquareAPIKey)

controller = Controller(client)
app = App(controller)

app.start()
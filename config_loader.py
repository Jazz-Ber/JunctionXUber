import json
import os

class ConfigLoader():
    def __init__(self, path):
        # Make path relative to the location of config_loader.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, path)
        self.path = full_path
        self.config = self._load_config(self.path)

    def _load_config(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                return json.load(file)
        else:
            raise FileNotFoundError(f"Config file {filename} not found")
    
    def get_key(self):
        # if self.config["fourSquareApiKey"] is not None:
        return self.config["fourSquareAPIKey"]
        # raise KeyError("Key 'fourSquareAPIKey' not found in config")
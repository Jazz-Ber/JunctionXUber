# The main controller script

import tkinter as tk

class Controller:
    def busy_address(self):
        return "Den Haag"
    
    def idle_address(self):
        return "Barendrecht"

if __name__ == "__main__":
    # Import here to avoid circular import
    from ui import App
    app = App()
    app.start()

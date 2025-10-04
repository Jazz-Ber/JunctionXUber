# controller.py
class Controller:
    def __init__(self):
        self.busy_address = "Den Haag"
        self.idle_address = "Barendrecht"

    # Methods to update addresses
    def set_busy_address(self, addr):
        self.busy_address = addr

    def set_idle_address(self, addr):
        self.idle_address = addr

    # Methods to get addresses
    def get_busy_address(self):
        return self.busy_address

    def get_idle_address(self):
        return self.idle_address

# self.py
class Controller:
    def __init__(self, client):
        self.busy_address = "Den Haag"
        self.idle_address = "Barendrecht"
        self.client = client


    def getLocations(self, current_coords):
        params = {
            "ll": f"{round(current_coords[0], 4)},{round(current_coords[1], 4)}",  # lat,lng # Should be coordinates that map is currently on.
            "radius": 2000,
            "limit": 20
        }

        response = self.client.getNearbyLocations(params)
        result = response.json().get("results", [])

        if len(result) > 1:
            busy_location = result[0].get("location", {})
            idle_location = result[1].get("location", {})

            self.set_busy_address(busy_location.get("formatted_address", self.get_busy_address()))
            self.set_idle_address(idle_location.get("formatted_address", self.get_idle_address()))

        # Print for debugging
        print("Busy:", self.get_busy_address())
        print("Idle:", self.get_idle_address())
        return result

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

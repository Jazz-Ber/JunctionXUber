import customtkinter
from tkintermapview import TkinterMapView
import requests
from controller import Controller

controller = Controller()

customtkinter.set_default_color_theme("blue")


def geocode_address(address):
    """Geocode an address using Nominatim with proper User-Agent header"""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        'User-Agent': 'JunctionXUber/1.0 (Educational Project)'
    }
    params = {
        'q': address,
        'format': 'jsonv2',
        'addressdetails': 1,
        'limit': 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
            else:
                print(f"No results found for address: {address}")
                return None
        else:
            print(f"Geocoding failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error geocoding address '{address}': {e}")
        return None


class App(customtkinter.CTk):

    APP_NAME = "TkinterMapView with CustomTkinter"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.marker_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(2, weight=1)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Find Busy Place",
                                                command=self.find_busy_place)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Find Idle Place",
                                                command=self.find_idle_place)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=(20, 20), pady=(10, 20))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search",
                                                width=90,
                                                command=self.search_event)
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Set default values
        # Use custom geocoding for default address
        delft_coords = geocode_address("Delft")
        if delft_coords:
            lat, lon = delft_coords
            self.map_widget.set_position(lat, lon, marker=True)
            self.map_widget.set_zoom(16)
        else:
            # Fallback to default coordinates for Delft
            self.map_widget.set_position(52.0116, 4.3571, marker=True)
            self.map_widget.set_zoom(16)
        
        self.appearance_mode_optionemenu.set("Dark")
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def search_event(self, event=None):
        address = self.entry.get().strip()
        self.search_event_with_address(address)

    def search_event_with_address(self, address):
        if address:
            # Use our custom geocoding function
            coordinates = geocode_address(address)
            if coordinates:
                self.map_widget.delete_all_marker()
                lat, lon = coordinates
                self.map_widget.set_position(lat, lon, marker=True)
                self.map_widget.set_zoom(15)
                print(f"Found address '{address}' at coordinates: {lat}, {lon}")
            else:
                print(f"Could not find coordinates for address: {address}")
        else:
            print("Please enter an address to search")

    def find_busy_place(self):
        busy_address = controller.busy_address()
        self.search_event_with_address(busy_address)

    def find_idle_place(self):
        idle_address = controller.idle_address()
        self.search_event_with_address(idle_address)

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()
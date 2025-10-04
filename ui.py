import customtkinter
from tkintermapview import TkinterMapView
import requests
import json
import math
from controller import Controller

# controller = Controller()

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


def get_driving_route(start_coords, end_coords):
    """Get driving route waypoints between two coordinates using OpenRouteService"""
    try:
        # Using OpenRouteService (free alternative to Google Maps API)
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        
        # OpenRouteService requires an API key, but you can use a free one
        # For demo purposes, we'll use a simple fallback
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8'
        }
        
        # Format: [longitude, latitude] for OpenRouteService
        body = {
            "coordinates": [
                [start_coords[1], start_coords[0]],  # [lon, lat]
                [end_coords[1], end_coords[0]]       # [lon, lat]
            ],
            "format": "geojson"
        }
        
        # For now, we'll use a simple fallback that creates intermediate waypoints
        # In a real implementation, you'd use a proper routing API with an API key
        print("Routing service not configured - using straight line path")
        return [start_coords, end_coords]
        
    except Exception as e:
        print(f"Error getting driving route: {e}")
        # Fallback to straight line
        return [start_coords, end_coords]


def get_driving_route_with_osrm(start_coords, end_coords):
    """Get driving route waypoints using OSRM (Open Source Routing Machine) - free service"""
    try:
        # OSRM public server - free but may have rate limits
        url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
        params = {
            'overview': 'full',
            'geometries': 'geojson'
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok' and data.get('routes'):
                # Extract coordinates from the route geometry
                coordinates = data['routes'][0]['geometry']['coordinates']
                distance = round(float(data['routes'][0]['legs'][0]['distance']) / 1000.0, 1)
                duration = math.ceil(float(data['routes'][0]['legs'][0]['duration']) / 60.0)
                # Convert from [lon, lat] to [lat, lon] format for tkintermapview
                waypoints = [(coord[1], coord[0]) for coord in coordinates]
                return waypoints, distance, duration
            else:
                print(f"OSRM routing failed: {data}")
                return [start_coords, end_coords], None, None
        else:
            print(f"OSRM request failed with status code: {response.status_code}")
            return [start_coords, end_coords], None, None
            
    except Exception as e:
        print(f"Error getting OSRM route: {e}")
        return [start_coords, end_coords], None, None


class App(customtkinter.CTk):

    APP_NAME = "Uber Driver Assitent"
    WIDTH = 800
    HEIGHT = 500
    current_location_marker = None
    current_location_coords = None

    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add controller as dependency
        self.controller = controller

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
                                                text="Find Busy Place", font=("Inter", 15),
                                                command=self.find_busy_place)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Find Idle Place", font=("Inter", 15),
                                                command=self.find_idle_place)
        self.button_2.grid(pady=(100, 0), padx=(20, 20), row=0, column=0)

        self.current_route_label = customtkinter.CTkLabel(self.frame_left, text="", font=("Inter", 18), anchor="w")
        self.current_route_label.grid(row=1, column=0, padx=(20, 20), pady=(20, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", font=("Inter", 15), anchor="w")
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
                                            placeholder_text="Type address...", font=("Inter", 12),)
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search", font=("Inter", 15),
                                                width=90,
                                                command=self.search_event)
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Set default values
        # Use custom geocoding for default address
        delft_coords = geocode_address("Delft")
        if delft_coords:
            lat, lon = delft_coords
            self.current_location_coords = (lat, lon)
            self.current_location_marker = self.map_widget.set_position(lat, lon, marker=True)
            self.map_widget.set_zoom(16)
        else:
            # Fallback to default coordinates for Delft
            self.current_location_coords = (52.0116, 4.3571)
            self.current_location_marker = self.map_widget.set_position(52.0116, 4.3571, marker=True)
            self.map_widget.set_zoom(16)
        
        self.appearance_mode_optionemenu.set("Dark")
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.add_right_click_menu_command(label="Route to here",
                                            command=self.add_route_event,
                                            pass_coords=True)

    def search_event(self, event=None):
        address = self.entry.get().strip()
        self.entry.delete(0, "end")
        self.search_event_with_address(address)

    def search_event_with_address(self, address):
        if address:
            # Use our custom geocoding function
            coordinates = geocode_address(address)
            if coordinates:
                self.map_widget.delete_all_marker()
                self.map_widget.delete_all_path()
                lat, lon = coordinates
                self.current_location_coords = (lat, lon)
                self.current_location_marker = self.map_widget.set_position(lat, lon, marker=True)
                self.map_widget.set_zoom(15)
                print(f"Found address '{address}' at coordinates: {lat}, {lon}")
            else:
                print(f"Could not find coordinates for address: {address}")
        else:
            print("Please enter an address to search")

    def find_busy_place(self):
        busy_address = self.controller.get_busy_address()
        if busy_address:
            coordinates = geocode_address(busy_address)
            if coordinates:
                self.map_widget.delete_all_marker()
                if self.current_location_coords:
                    self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
                self.map_widget.delete_all_path()

                lat, lon = coordinates
                busy_area_marker = self.map_widget.set_position(lat, lon, marker=True)
                self.map_widget.set_zoom(15)
                
                # Get actual driving route instead of straight line
                if self.current_location_coords:
                    route_waypoints, distance, duration = get_driving_route_with_osrm(self.current_location_coords, (lat, lon))
                    self.current_route_label.configure(text=f"Current Route:\n\nDistance: {distance} km\nDuration: {duration} minutes")
                    busy_path = self.map_widget.set_path(route_waypoints)
                    print(f"Generated driving route with {len(route_waypoints)} waypoints")
                
                print(f"Found address '{busy_address}' at coordinates: {lat}, {lon}")
            else:
                print(f"Could not find coordinates for address: {busy_address}")
        else:
            print("Please enter an address to search")

    def find_idle_place(self):
        idle_address = self.controller.get_idle_address()
        if idle_address:
            coordinates = geocode_address(idle_address)
            if coordinates:
                self.map_widget.delete_all_marker()
                if self.current_location_coords:
                    self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
                self.map_widget.delete_all_path()
                
                lat, lon = coordinates
                idle_area_marker = self.map_widget.set_position(lat, lon, marker=True)
                self.map_widget.set_zoom(15)
                
                # Get actual driving route instead of straight line
                if self.current_location_coords:
                    route_waypoints, distance, duration = get_driving_route_with_osrm(self.current_location_coords, (lat, lon))
                    self.current_route_label.configure(text=f"Current Route:\n\nDistance: {distance} km\nDuration: {duration} minutes")
                    idle_path = self.map_widget.set_path(route_waypoints)
                    print(f"Generated driving route with {len(route_waypoints)} waypoints")
                
                print(f"Found address '{idle_address}' at coordinates: {lat}, {lon}")
            else:
                print(f"Could not find coordinates for address: {idle_address}")
        else:
            print("Please enter an address to search")

    def add_route_event(self, coords):
        print("Add marker:", coords)
        self.map_widget.delete_all_marker()
        if self.current_location_coords:
            self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
        self.map_widget.delete_all_path()

        lat, lon = coords
        new_area_marker = self.map_widget.set_marker(lat, lon)

        # Get actual driving route instead of straight line
        if self.current_location_coords:
            route_waypoints, distance, duration = get_driving_route_with_osrm(self.current_location_coords, (lat, lon))
            self.current_route_label.configure(text=f"Current Route:\n\nDistance: {distance} km\nDuration: {duration} minutes")
            busy_path = self.map_widget.set_path(route_waypoints)
            print(f"Generated driving route with {len(route_waypoints)} waypoints")
        
        print(f"Setting route to coordinates: {lat}, {lon}")

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()
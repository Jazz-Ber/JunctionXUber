import customtkinter
from tkintermapview import TkinterMapView
import requests
import json
import math
import threading
from controller import Controller
from process_logic import ProcessLogic

customtkinter.set_default_color_theme("blue")

def calculate_cluster_radius(cluster_locations, center_coords, total_locations):
    """
    Calculate an appropriate radius for a cluster based on its spread.
    
    Args:
        cluster_locations (list): List of (lat, lon) tuples in the cluster
        center_coords (tuple): Center coordinates as (latitude, longitude)
    
    Returns:
        float: Radius in kilometers
    """
    if len(cluster_locations) <= 1:
        return 0.5
    
    radius = 0.3 + (1.7 - 0.3) * math.log(len(cluster_locations)) / math.log(total_locations)
    return radius

def create_circular_polygon(center_coords, radius_km=0.5, num_points=20):
    """
    Create a circular polygon around a center point for map visualization.
    
    Args:
        center_coords (tuple): Center coordinates as (latitude, longitude)
        radius_km (float): Radius of the circle in kilometers (default: 0.5 km)
        num_points (int): Number of points to approximate the circle (default: 20)
    
    Returns:
        list: List of (lat, lon) tuples forming a circular polygon
    """
    lat, lon = center_coords
    
    # Convert radius from km to degrees (approximate)
    # 1 degree of latitude ≈ 111 km
    # 1 degree of longitude ≈ 111 km * cos(latitude)
    radius_lat = radius_km / 111.0
    radius_lon = radius_km / (111.0 * math.cos(math.radians(lat)))
    
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Calculate offset from center
        delta_lat = radius_lat * math.cos(angle)
        delta_lon = radius_lon * math.sin(angle)
        
        # Add to center coordinates
        point_lat = lat + delta_lat
        point_lon = lon + delta_lon
        
        points.append((point_lat, point_lon))
    
    return points

def get_driving_route(start_coords, end_coords):
    """
    Get driving route waypoints between two coordinates using OpenRouteService.
    
    This function is intended to use the OpenRouteService API for route calculation
    but currently returns a simple fallback route due to missing API key configuration.
    
    Args:
        start_coords (tuple): Starting coordinates as (latitude, longitude)
        end_coords (tuple): Destination coordinates as (latitude, longitude)
    
    Returns:
        list: A list containing only the start and end coordinates as a fallback
              In a full implementation, would return detailed waypoints along the route
    
    Notes:
        - Currently uses a fallback implementation that returns straight line
        - OpenRouteService requires API key registration for full functionality
        - The headers and body structure are prepared for actual API usage
        - Coordinate format for OpenRouteService is [longitude, latitude]
    
    Example:
        >>> start = (52.0116, 4.3571)  # Delft
        >>> end = (52.3676, 4.9041)    # Amsterdam
        >>> route = get_driving_route(start, end)
        >>> print(route)
        [(52.0116, 4.3571), (52.3676, 4.9041)]
    """
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
        params = {
            'overview': 'full',
            'geometries': 'geojson'
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok' and data.get('routes'):
                coordinates = data['routes'][0]['geometry']['coordinates']
                distance = round(float(data['routes'][0]['legs'][0]['distance']) / 1000.0, 1)
                duration = math.ceil(float(data['routes'][0]['legs'][0]['duration']) / 60.0)
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

    APP_NAME = "Uber Driver Assistant"
    WIDTH = 800
    HEIGHT = 500
    current_location_marker = None
    current_location_coords = None
    process_logic = ProcessLogic()
    is_processing = False

    def __init__(self, controller, *args, **kwargs):
        """
        Initialize the window
        """
        super().__init__(*args, **kwargs)

        self.controller = controller

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.marker_list = []

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        self.frame_left.grid_rowconfigure(2, weight=1)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Find Busy Place", font=("Inter", 15),
                                                command=self.find_busy_place)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Find Idle Place", font=("Inter", 15),
                                                command=self.find_idle_place)
        self.button_2.grid(pady=(100, 0), padx=(20, 20), row=0, column=0)

        self.current_route_label = customtkinter.CTkLabel(self.frame_left, text="", font=("Inter", 18), anchor="w", wraplength=150, justify="center")
        self.current_route_label.grid(row=1, column=0, padx=(20, 20), pady=(20, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", font=("Inter", 15), anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=(20, 20), pady=(10, 20))

        self.status_label = customtkinter.CTkLabel(self.frame_left, text="Status:\nReady", font=("Inter", 12), anchor="w", text_color="LemonChiffon3", wraplength=150, justify="center")
        self.status_label.grid(row=3, column=0, padx=(20, 20), pady=(10, 0))

        self.help_button = customtkinter.CTkButton(master=self, text="?", font=("Inter", 16, "bold"), 
                                                 width=30, height=30, command=self.show_help)
        self.help_button.grid(row=0, column=1, padx=20, pady=10, sticky="ne")

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

        delft_coords = (52.01173610138923, 4.359210368076695)
        if delft_coords:
            lat, lon = delft_coords
            self.current_location_coords = (lat, lon)
            self.current_location_marker = self.map_widget.set_position(lat, lon, marker=True)
            self.map_widget.set_zoom(16)
        else:
            self.current_location_coords = (52.0116, 4.3571)
            self.current_location_marker = self.map_widget.set_position(52.0116, 4.3571, marker=True)
            self.map_widget.set_zoom(16)
        
        self.appearance_mode_optionemenu.set("Dark")
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.add_right_click_menu_command(label="Route to here",
                                            command=self.add_route_event,
                                            pass_coords=True)
        self.map_widget.add_right_click_menu_command(label="Set location here",
                                            command=self.search_event_with_address,
                                            pass_coords=True)
                                            

    def _set_buttons_loading_state(self, is_loading=True):
        """
        Sets the button from false to true or the other way around
        """
        if is_loading:
            self.is_processing = True
            self.button_1.configure(state="disabled", text="Processing...")
            self.button_2.configure(state="disabled", text="Processing...")
        else:
            self.is_processing = False
            self.button_1.configure(state="normal", text="Find Busy Place")
            self.button_2.configure(state="normal", text="Find Idle Place")

    def click_busy_area(self, polygon):
        if not polygon or not polygon.position_list:
            self.map_widget.delete_all_polygon()
            self.update_status("Failed to route to area.")
            return

        busy_address = self.process_logic.cluster_average(polygon.position_list)

        self.map_widget.delete_all_polygon()
        self._update_map_for_busy_place(busy_address)

    def click_idle_area(self, polygon):
        if not polygon or not polygon.position_list:
            self.map_widget.delete_all_polygon()
            self.update_status("Failed to route to area.")
            return

        busy_address = self.process_logic.cluster_average(polygon.position_list)
        idle_address = self.controller.get_idling_place(busy_address)

        self.map_widget.delete_all_polygon()
        self._update_map_for_idle_place(idle_address)

    def update_status(self, message):
        """Update the status label with a new message"""
        self.status_label.configure(text=f"Status:\n{message}")
        self.update()

    def show_help(self):
        """Show help window with app instructions"""
        help_window = customtkinter.CTkToplevel(self)
        help_window.title("Help - Uber Driver Assistant")
        help_window.geometry("500x600")
        help_window.resizable(False, False)
        
        help_window.transient(self)
        help_window.grab_set()
        
        help_text = """
Uber Driver Assistant - Help

OVERVIEW:
This app helps Uber Earners find the best locations to pick up passengers by analyzing busy and idle areas.

HOW TO USE:

1. SEARCH FOR LOCATION:
   • Type an address in the search box
   • Press Enter or click Search
   • The map will center on your location

2. FIND BUSY PLACES:
   • Click the "Find Busy Place" button
   • The app will show clusters of high-demand areas
   • Click on any cluster to get directions there
   • Green circles show busy areas with passenger counts

3. FIND IDLE PLACES:
   • Click the "Find Idle Place" button  
   • The app will show clusters of high-demand areas
   • Click on any cluster to get directions to a parking lot nearest to the busy area
   • Perfect place to wait or rest in between rides
   • Click on any cluster to get directions there

4. INTERACTIVE MAP:
   • Right-click anywhere on map to select starting location
   • Zoom in/out with mouse wheel
   • Drag to pan around the map

5. STATUS INDICATORS:
   • Status shows what the program is currently doing
   • "Location too remote" means no data available for that location
   • Route info shows distance and travel time

TIPS:
• Search for major cities for best results
• Distance and busyness info shown on markers
• Use appearance mode to switch themes

TROUBLESHOOTING:
• If no results found, try a different location
• Ensure you have internet connection
• Remote areas may not have enough data. 
  Getting closer to a major city is recommended
        """
        
        text_frame = customtkinter.CTkFrame(help_window)
        text_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        text_widget = customtkinter.CTkTextbox(text_frame, font=("Inter", 12))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", help_text)
        text_widget.configure(state="disabled")
        
        close_button = customtkinter.CTkButton(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)

    def _find_busy_place_threaded(self):
        """
        Finds the busiest place near the current location in a separate thread,
        updates the map with the result, and manages button loading states.
        """
        try:
            self.after(0, self.update_status, "Finding busy places...")
            
            locations = self.controller.getLocations(self.current_location_coords)
            self.after(0, self.update_status, "Analyzing locations...")
            
            clusters = self.process_logic.cluster_maker(locations)

            total_locations = len(locations)
            self.map_widget.delete_all_marker()
            self.map_widget.delete_all_path()
            self.map_widget.delete_all_polygon()
            self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
            for cluster in clusters:
                cluster_locations = cluster[0]
                cluster_center = cluster[1]
                
                radius = calculate_cluster_radius(cluster_locations, cluster_center, total_locations)
                name = f"Busyness: {len(cluster_locations)}\nDistance: {round(self.process_logic.distance_finder(self.current_location_coords, cluster_center), 1)} km"

                circle_points = create_circular_polygon(cluster_center, radius_km=radius)
                self.map_widget.set_polygon(circle_points, command=self.click_busy_area, fill_color="aquamarine2", outline_color="firebrick2")
                self.map_widget.set_marker(cluster_center[0], cluster_center[1], text=name, font=("Inter", 18), marker_color_circle="dodgerblue4", marker_color_outside="steelblue")

            self.after(0, self.update_status, "Calculating busy areas...")

            if clusters:
                self.after(0, self.update_status, "Route calculated")
                self.current_route_label.configure(text="Click an area to route to there")
            else:
                self.after(0, self.update_status, "Busy location too remote")
                print("No busy places found - location too remote")
                
        except Exception as e:
            self.after(0, self.update_status, f"Error: {str(e)}")
            print(f"Error finding busy place: {e}")
        finally:
            self.after(0, self._set_buttons_loading_state, False)

    def _find_idle_place_threaded(self):
        """
        Finds the best place to sit idle while waiting for requests in a separate thread,
        Updates the map with the result, and manages button loading states.
        """
        try:
            self.after(0, self.update_status, "Finding idle places...")
            
            locations = self.controller.getLocations(self.current_location_coords)
            self.after(0, self.update_status, "Analyzing locations...")
            
            clusters = self.process_logic.cluster_maker(locations)
            self.after(0, self.update_status, "Calculating idle areas...")

            total_locations = len(locations)
            self.map_widget.delete_all_marker()
            self.map_widget.delete_all_path()
            self.map_widget.delete_all_polygon()
            self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
            for cluster in clusters:
                cluster_locations = cluster[0]
                cluster_center = cluster[1]
                
                radius = calculate_cluster_radius(cluster_locations, cluster_center, total_locations)
                
                name = f"Busyness: {len(cluster_locations)}\nDistance: {round(self.process_logic.distance_finder(self.current_location_coords, cluster_center), 1)} km"

                circle_points = create_circular_polygon(cluster_center, radius_km=radius)
                self.map_widget.set_polygon(circle_points, command=self.click_idle_area, fill_color="aquamarine2", outline_color="firebrick2")
                self.map_widget.set_marker(cluster_center[0], cluster_center[1], text=name, font=("Inter", 18), marker_color_circle="dodgerblue4", marker_color_outside="steelblue")
            
            if clusters:
                self.after(0, self.update_status, "Route calculated")
                self.current_route_label.configure(text="Click an area to route to there")
            else:
                self.after(0, self.update_status, "Idle location too remote")
                print("No idle places found - location too remote")
                
        except Exception as e:
            self.after(0, self.update_status, f"Error: {str(e)}")
            print(f"Error finding idle place: {e}")
        finally:
            self.after(0, self._set_buttons_loading_state, False)

    def _update_map_for_busy_place(self, busy_address):
        """
        Update the map with the new busy adress and the route between current location and the new busy address
        """
        if not idle_address:
            self.update_status("Error finding place, please try again.")
            return

        self.map_widget.delete_all_marker()
        if self.current_location_coords:
            self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
        self.map_widget.delete_all_path()

        lat, lon = busy_address
        busy_area_marker = self.map_widget.set_position(lat, lon, marker=True, marker_color_circle="dodgerblue4", marker_color_outside="steelblue")
        self.map_widget.set_zoom(15)
        
        if self.current_location_coords:
            route_waypoints, distance, duration = get_driving_route(self.current_location_coords, (lat, lon))
            self.current_route_label.configure(text=f"Current Route:\n\nDistance: {distance} km\nDuration: {duration} minutes")
            busy_path = self.map_widget.set_path(route_waypoints)
            print(f"Generated driving route with {len(route_waypoints)} waypoints")


    def _update_map_for_idle_place(self, idle_address):
        """
        Update the map with the new idle address and the route between current location and the new idle address
        """
        if not idle_address:
            self.update_status("Error finding place, please try again.")
            return

        self.map_widget.delete_all_marker()
        if self.current_location_coords:
            self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
        self.map_widget.delete_all_path()
        
        lat, lon = idle_address
        idle_area_marker = self.map_widget.set_position(lat, lon, marker=True, marker_color_circle="dodgerblue4", marker_color_outside="steelblue")
        self.map_widget.set_zoom(15)
        
        if self.current_location_coords:
            route_waypoints, distance, duration = get_driving_route(self.current_location_coords, (lat, lon))
            self.current_route_label.configure(text=f"Current Route:\n\nDistance: {distance} km\nDuration: {duration} minutes")
            idle_path = self.map_widget.set_path(route_waypoints)
            print(f"Generated driving route with {len(route_waypoints)} waypoints")
        
        print(f"Found address '{idle_address}' at coordinates: {lat}, {lon}")

    def search_event(self, event=None):
        """
        Searches for own location from inputted address
        """
        address = self.entry.get().strip()
        self.entry.delete(0, "end")
        self.search_event_with_address(address)

    def geocode_address(self, address):
        """
        Gets the longitude and latitude from the given address
        """
        if isinstance(address, tuple):
            return address

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

    def search_event_with_address(self, address):
        """
        Gets the coordinates with the adress and sets its marker at the place where we now are
        """
        if address:
            self.update_status("Searching for address...")
            coordinates = self.geocode_address(address)
            if coordinates:
                self.map_widget.delete_all_marker()
                self.map_widget.delete_all_path()
                self.map_widget.delete_all_polygon()
                self.current_route_label.configure(text="")
                lat, lon = coordinates
                self.current_location_coords = (lat, lon)
                self.current_location_marker = self.map_widget.set_position(lat, lon, marker=True)
                self.map_widget.set_zoom(15)
                self.update_status("Location found")
                print(f"Found address '{address}' at coordinates: {lat}, {lon}")
            else:
                self.update_status("Location too remote - no results found")
                print(f"Could not find coordinates for address: {address}")
        else:
            self.update_status("Please enter an address\nto search")
            print("Please enter an address to search")

    def find_busy_place(self):
        if self.is_processing:
            return
            
        self.update_status("Starting search...")
        self._set_buttons_loading_state(True)
        
        thread = threading.Thread(target=self._find_busy_place_threaded, daemon=True)
        thread.start()

    def find_idle_place(self):
        if self.is_processing:
            return
            
        self.update_status("Starting search...")
        self._set_buttons_loading_state(True)
        
        thread = threading.Thread(target=self._find_idle_place_threaded, daemon=True)
        thread.start()

    def add_route_event(self, coords):
        """
        Adds a route to the UI when finding a new idle or busy location
        """
        if not coords:
            self.update_status("Unexpected error, please try again.")
            return

        print("Add marker:", coords)
        self.map_widget.delete_all_marker()
        if self.current_location_coords:
            self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
        self.map_widget.delete_all_path()

        lat, lon = coords
        new_area_marker = self.map_widget.set_marker(lat, lon, marker_color_circle="dodgerblue4", marker_color_outside="steelblue")

        if self.current_location_coords:
            route_waypoints, distance, duration = get_driving_route(self.current_location_coords, (lat, lon))
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
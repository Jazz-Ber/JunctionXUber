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
        return 0.5  # Minimum radius for single points
    
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
    """
    Get driving route waypoints using OSRM (Open Source Routing Machine) - free service.
    
    This function queries the OSRM public API to calculate the optimal driving route
    between two geographical coordinates. It returns detailed route information including
    waypoints, distance, and estimated duration.
    
    Args:
        start_coords (tuple): Starting coordinates as (latitude, longitude)
        end_coords (tuple): Destination coordinates as (latitude, longitude)
    
    Returns:
        tuple: A 3-tuple containing:
            - waypoints (list): List of (lat, lon) coordinate tuples representing the route path
            - distance (float): Total route distance in kilometers, rounded to 1 decimal place
            - duration (int): Estimated travel time in minutes, rounded up to nearest minute
            
        If the API call fails or returns an error, returns:
            ([start_coords, end_coords], None, None)
    
    Notes:
        - Uses the free OSRM public server (router.project-osrm.org)
        - The public server may have rate limits and availability constraints
        - Coordinates are converted from OSRM's [longitude, latitude] format to 
          tkintermapview's [latitude, longitude] format
        - Has a 10-second timeout for API requests
        - Falls back to a straight line between start and end points if routing fails
    
    Example:
        >>> start = (52.0116, 4.3571)  # Delft, Netherlands
        >>> end = (52.3676, 4.9041)    # Amsterdam, Netherlands
        >>> waypoints, distance, duration = get_driving_route_with_osrm(start, end)
        >>> print(f"Route: {len(waypoints)} waypoints, {distance}km, {duration}min")
        Route: 156 waypoints, 58.2km, 67min
    
    Raises:
        No exceptions are raised directly - all errors are caught and logged,
        with fallback values returned instead.
    """
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

    APP_NAME = "Uber Driver Assistant"
    WIDTH = 800
    HEIGHT = 500
    current_location_marker = None
    current_location_coords = None
    process_logic = ProcessLogic()
    is_processing = False  # Track if any operation is running

    def __init__(self, controller, *args, **kwargs):
        """
        Initialize the Uber Driver Assistant application window.
        
        Sets up the main GUI window with a two-panel layout: a left control panel
        with action buttons and settings, and a right panel with an interactive map.
        Configures the map with default location (Delft, Netherlands) and sets up
        event handlers for user interactions.
        
        Args:
            controller: Controller instance that handles business logic and data operations
            *args: Variable length argument list passed to parent CTk constructor
            **kwargs: Arbitrary keyword arguments passed to parent CTk constructor
        
        Attributes Created:
            controller: Reference to the controller for business logic operations
            marker_list (list): List to store map markers
            frame_left (CTkFrame): Left panel containing control buttons and settings
            frame_right (CTkFrame): Right panel containing the map widget
            button_1 (CTkButton): "Find Busy Place" action button
            button_2 (CTkButton): "Find Idle Place" action button
            current_route_label (CTkLabel): Label displaying current route information
            appearance_mode_optionemenu (CTkOptionMenu): Theme selection dropdown
            map_widget (TkinterMapView): Interactive map component
            entry (CTkEntry): Address search input field
            button_5 (CTkButton): Search button for address lookup
        
        Side Effects:
            - Sets window title, size, and minimum dimensions
            - Configures window close protocol
            - Sets up grid layout with proper column/row weights
            - Initializes map with Delft coordinates and Google Maps tiles
            - Sets appearance mode to "Dark"
            - Adds right-click context menu to map for route creation
        
        Example:
            >>> from controller import Controller
            >>> ctrl = Controller()
            >>> app = App(ctrl)
            >>> app.start()  # Launches the GUI
        """
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

        self.status_label = customtkinter.CTkLabel(self.frame_left, text="Status:\nReady", font=("Inter", 12), anchor="w", text_color="MistyRose3")
        self.status_label.grid(row=3, column=0, padx=(20, 20), pady=(10, 0))


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
        delft_coords = (52.01173610138923, 4.359210368076695)
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

    def _set_buttons_loading_state(self, is_loading=True):
        """Enable or disable both action buttons and show loading state"""
        if is_loading:
            self.is_processing = True
            self.button_1.configure(state="disabled", text="Processing...")
            self.button_2.configure(state="disabled", text="Processing...")
        else:
            self.is_processing = False
            self.button_1.configure(state="normal", text="Find Busy Place")
            self.button_2.configure(state="normal", text="Find Idle Place")

    def click_busy_area(self, polygon):
        if not polygon.position_list:
            self.map_widget.delete_all_polygon()
            # TODO: parse error
            return

        busy_address = self.process_logic.cluster_average(polygon.position_list)

        self.map_widget.delete_all_polygon()
        self._update_map_for_busy_place(busy_address)

    def update_status(self, message):
        """Update the status label with a new message"""
        self.status_label.configure(text=f"Status:\n{message}")
        self.update()  # Force immediate UI update

    def _find_busy_place_threaded(self):
        """
        Threaded version of find_busy_place - runs in background.
        
        Executes the busy place finding algorithm in a separate thread to prevent
        GUI freezing during computation. Retrieves locations, performs clustering
        analysis, and identifies the busiest area near the current location.
        Updates the UI with results via thread-safe callbacks.
        
        Args:
            None (uses self.current_location_coords for location context)
        
        Returns:
            None (results are passed to UI update methods via self.after())
        
        Side Effects:
            - Calls controller.getLocations() to fetch location data
            - Performs clustering analysis via process_logic.cluster_maker()
            - Identifies busy address via controller.get_busy_address()
            - Schedules UI update in main thread if busy place is found
            - Always restores button state regardless of success/failure
            - Prints error messages to console on exceptions
        
        Thread Safety:
            - Designed to run in background thread (daemon=True)
            - Uses self.after() to schedule UI updates in main thread
            - Exception handling ensures button state is always restored
        
        Notes:
            - This method should only be called from threading.Thread
            - Requires self.current_location_coords to be set
            - Results in map update showing route to busy location
        
        Example:
            >>> thread = threading.Thread(target=app._find_busy_place_threaded, daemon=True)
            >>> thread.start()
        """
        try:
            self.after(0, self.update_status, "Finding busy places...")
            
            locations = self.controller.getLocations(self.current_location_coords)
            self.after(0, self.update_status, "Analyzing locations...")
            
            clusters = self.process_logic.cluster_maker(locations)

            total_locations = len(locations)
            self.map_widget.delete_all_polygon()
            for cluster in clusters:
                # cluster[0] = list of locations, cluster[1] = center coordinates
                cluster_locations = cluster[0]
                cluster_center = cluster[1]
                
                # Calculate appropriate radius based on cluster spread
                radius = calculate_cluster_radius(cluster_locations, cluster_center, total_locations)
                
                # Create a name
                name = f"Busyness: {len(cluster_locations)}\nDistance: {round(self.process_logic.distance_finder(self.current_location_coords, cluster_center), 1)} km"

                # Create circular polygon around the center
                circle_points = create_circular_polygon(cluster_center, radius_km=radius)
                self.map_widget.set_polygon(circle_points, command=self.click_busy_area, fill_color="aquamarine2", outline_color="firebrick2")
                self.map_widget.set_marker(cluster_center[0], cluster_center[1], text=name, font=("Inter", 18), marker_color_circle="dodgerblue4", marker_color_outside="steelblue")

            self.after(0, self.update_status, "Calculating busy areas...")

            if clusters:
                self.after(0, self.update_status, "Route calculated")
            else:
                self.after(0, self.update_status, "Busy location too remote")
                print("No busy places found - location too remote")
                
        except Exception as e:
            self.after(0, self.update_status, f"Error: {str(e)}")
            print(f"Error finding busy place: {e}")
        finally:
            # Always restore button state in main thread
            self.after(0, self._set_buttons_loading_state, False)

    def _find_idle_place_threaded(self):
        """
        Threaded version of find_idle_place - runs in background.
        
        Executes the idle place finding algorithm in a separate thread to prevent
        GUI freezing during computation. Identifies areas with low activity or
        demand that might be good for drivers to wait for rides.
        Updates the UI with results via thread-safe callbacks.
        
        Args:
            None (uses controller methods that may have their own location logic)
        
        Returns:
            None (results are passed to UI update methods via self.after())
        
        Side Effects:
            - Calls controller.get_idle_address() to find low-activity areas
            - Schedules UI update in main thread if idle place is found
            - Always restores button state regardless of success/failure
            - Prints error messages to console on exceptions
        
        Thread Safety:
            - Designed to run in background thread (daemon=True)
            - Uses self.after() to schedule UI updates in main thread
            - Exception handling ensures button state is always restored
        
        Notes:
            - This method should only be called from threading.Thread
            - Currently passes None to get_idle_address() - may need location context
            - Results in map update showing route to idle location
            - There appears to be a bug: 'coordinates' variable is undefined in line 213
        
        Example:
            >>> thread = threading.Thread(target=app._find_idle_place_threaded, daemon=True)
            >>> thread.start()
        """
        try:
            self.after(0, self.update_status, "Finding idle places...")
            
            locations = self.controller.getLocations(self.current_location_coords)
            self.after(0, self.update_status, "Analyzing locations...")
            
            clusters = self.process_logic.cluster_maker(locations)
            self.after(0, self.update_status, "Calculating idle areas...")
            
            idle_address = self.controller.get_idle_address(clusters, self.current_location_coords)
            if idle_address:
                self.after(0, self.update_status, "Route calculated")
                self.after(0, self._update_map_for_idle_place, idle_address)
            else:
                self.after(0, self.update_status, "Idle location too remote")
                print("No idle places found - location too remote")
                
        except Exception as e:
            self.after(0, self.update_status, f"Error: {str(e)}")
            print(f"Error finding idle place: {e}")
        finally:
            # Always restore button state in main thread
            self.after(0, self._set_buttons_loading_state, False)

    def _update_map_for_busy_place(self, busy_address):
        """
        Update map UI for busy place (runs in main thread).
        
        Updates the map display to show the route from current location to the
        identified busy place. Clears existing markers and paths, then displays
        the new route with driving directions, distance, and duration information.
        
        Args:
            busy_address (tuple): Coordinates of the busy place as (latitude, longitude)
        
        Returns:
            None
        
        Side Effects:
            - Clears all existing markers and paths from the map
            - Adds marker for current location if available
            - Sets new marker at busy place with blue styling
            - Calculates and displays driving route using OSRM
            - Updates route label with distance and duration information
            - Sets map zoom level to 15 for optimal viewing
            - Prints route generation information to console
        
        UI Updates:
            - Map markers: current location (default style) + busy place (blue)
            - Map path: driving route with multiple waypoints
            - Route label: "Current Route:\n\nDistance: X km\nDuration: Y minutes"
            - Map zoom: set to level 15
        
        Notes:
            - This method must run in the main thread for GUI updates
            - Called via self.after() from background threads
            - Requires self.current_location_coords to be set for route calculation
            - Uses get_driving_route_with_osrm() for realistic driving directions
        
        Example:
            >>> busy_coords = (52.0200, 4.3600)  # Some busy location
            >>> app._update_map_for_busy_place(busy_coords)
        """
        self.map_widget.delete_all_marker()
        if self.current_location_coords:
            self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
        self.map_widget.delete_all_path()

        lat, lon = busy_address
        busy_area_marker = self.map_widget.set_position(lat, lon, marker=True, marker_color_circle="dodgerblue4", marker_color_outside="steelblue")
        self.map_widget.set_zoom(15)
        
        # Get actual driving route instead of straight line
        if self.current_location_coords:
            route_waypoints, distance, duration = get_driving_route_with_osrm(self.current_location_coords, (lat, lon))
            self.current_route_label.configure(text=f"Current Route:\n\nDistance: {distance} km\nDuration: {duration} minutes")
            busy_path = self.map_widget.set_path(route_waypoints)
            print(f"Generated driving route with {len(route_waypoints)} waypoints")


    def _update_map_for_idle_place(self, idle_address):
        """
        Update map UI for idle place (runs in main thread).
        
        Updates the map display to show the route from current location to the
        identified idle place. Similar to busy place update but for low-activity
        areas where drivers might wait for rides. Clears existing display and
        shows new route with driving directions.
        
        Args:
            coordinates (tuple): Coordinates of the idle place as (latitude, longitude)
            idle_address (str): Human-readable address or description of the idle place
        
        Returns:
            None
        
        Side Effects:
            - Clears all existing markers and paths from the map
            - Adds marker for current location if available
            - Sets new marker at idle place with blue styling
            - Calculates and displays driving route using OSRM
            - Updates route label with distance and duration information
            - Sets map zoom level to 15 for optimal viewing
            - Prints route generation and address information to console
        
        UI Updates:
            - Map markers: current location (default style) + idle place (blue)
            - Map path: driving route with multiple waypoints
            - Route label: "Current Route:\n\nDistance: X km\nDuration: Y minutes"
            - Map zoom: set to level 15
        
        Notes:
            - This method must run in the main thread for GUI updates
            - Called via self.after() from background threads
            - Requires self.current_location_coords to be set for route calculation
            - Uses get_driving_route_with_osrm() for realistic driving directions
            - Prints both coordinates and human-readable address for debugging
        
        Example:
            >>> idle_coords = (52.0100, 4.3500)
            >>> idle_addr = "Quiet residential area near park"
            >>> app._update_map_for_idle_place(idle_coords, idle_addr)
        """

        self.map_widget.delete_all_marker()
        if self.current_location_coords:
            self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
        self.map_widget.delete_all_path()
        
        lat, lon = idle_address
        idle_area_marker = self.map_widget.set_position(lat, lon, marker=True, marker_color_circle="dodgerblue4", marker_color_outside="steelblue")
        self.map_widget.set_zoom(15)
        
        # Get actual driving route instead of straight line
        if self.current_location_coords:
            route_waypoints, distance, duration = get_driving_route_with_osrm(self.current_location_coords, (lat, lon))
            self.current_route_label.configure(text=f"Current Route:\n\nDistance: {distance} km\nDuration: {duration} minutes")
            idle_path = self.map_widget.set_path(route_waypoints)
            print(f"Generated driving route with {len(route_waypoints)} waypoints")
        
        print(f"Found address '{idle_address}' at coordinates: {lat}, {lon}")

    def search_event(self, event=None):
        """
        Handle search button click or Enter key press in address field.
        
        Retrieves the address text from the search entry field, clears the field,
        and delegates the actual search operation to search_event_with_address().
        This method serves as an event handler for both button clicks and keyboard events.
        
        Args:
            event (tkinter.Event, optional): Event object from tkinter (unused but required
                                           for event handler compatibility). Defaults to None.
        
        Returns:
            None
        
        Side Effects:
            - Retrieves text from self.entry widget and strips whitespace
            - Clears the entry field after retrieving the text
            - Calls search_event_with_address() with the retrieved address
        
        Event Binding:
            - Bound to self.entry "<Return>" event (Enter key press)
            - Bound to self.button_5 command (Search button click)
        
        Notes:
            - This is a thin wrapper around search_event_with_address()
            - The event parameter is required for tkinter event binding but not used
            - Automatically clears the search field after each search
        
        Example:
            >>> # User types "Amsterdam" and presses Enter
            >>> # This method is automatically called with event object
            >>> app.search_event()  # Searches for "Amsterdam" and clears field
        """
        address = self.entry.get().strip()
        self.entry.delete(0, "end")
        self.search_event_with_address(address)

    def geocode_address(self, address):
        """
        Geocode an address using Nominatim with proper User-Agent header.
        
        Converts a human-readable address string into geographic coordinates
        using the OpenStreetMap Nominatim geocoding service. Includes proper
        headers to comply with Nominatim usage policies.
        
        Args:
            address (str): Human-readable address to geocode (e.g., "Amsterdam, Netherlands")
        
        Returns:
            tuple or None: If successful, returns (latitude, longitude) as float tuple.
                          If geocoding fails or no results found, returns None.
        
        Side Effects:
            - Makes HTTP GET request to Nominatim API
            - Prints error messages to console on failures
            - Prints "No results found" message if address not found
        
        API Details:
            - Uses OpenStreetMap Nominatim service (free, no API key required)
            - Includes proper User-Agent header for educational project identification
            - Requests JSONv2 format with address details
            - Limits results to 1 (most relevant match)
            - Has 10-second timeout for requests
        
        Error Handling:
            - Network errors: caught and logged, returns None
            - HTTP errors: status code logged, returns None
            - JSON parsing errors: caught and logged, returns None
            - Empty results: logged message, returns None
        
        Notes:
            - Complies with Nominatim usage policy by including User-Agent
            - Uses educational project identifier in User-Agent string
            - Only returns the first (most relevant) result
        
        Example:
            >>> coords = app.geocode_address("Delft, Netherlands")
            >>> print(coords)
            (52.0116, 4.3571)
            
            >>> coords = app.geocode_address("NonexistentPlace123")
            No results found for address: NonexistentPlace123
            >>> print(coords)
            None
        """
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
        Perform address search and update map location.
        
        Takes a human-readable address, geocodes it to coordinates, and updates
        the map to show the new location. Clears existing markers and paths,
        then centers the map on the found location with a marker.
        
        Args:
            address (str): Address string to search for and display on map
        
        Returns:
            None
        
        Side Effects:
            - Calls geocode_address() to convert address to coordinates
            - Clears all existing markers and paths from map
            - Updates self.current_location_coords with new coordinates
            - Sets new map position with marker at found location
            - Updates self.current_location_marker reference
            - Sets map zoom level to 15 for detailed view
            - Prints success/failure messages to console
        
        Behavior:
            - If address is empty: prints "Please enter an address to search"
            - If geocoding succeeds: updates map and prints coordinates
            - If geocoding fails: prints error message, map unchanged
        
        Map Updates:
            - All existing markers and paths are cleared
            - New marker placed at geocoded coordinates
            - Map centered and zoomed to level 15 on new location
            - Current location coordinates updated for future route calculations
        
        Notes:
            - This method handles the actual search logic after address extraction
            - Updates the application's current location context
            - Used by both manual search and programmatic location setting
        
        Example:
            >>> app.search_event_with_address("Amsterdam Central Station")
            Found address 'Amsterdam Central Station' at coordinates: 52.3791, 4.9003
            
            >>> app.search_event_with_address("")
            Please enter an address to search
        """
        if address:
            # Use our custom geocoding function
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
        # Prevent multiple simultaneous executions
        if self.is_processing:
            return
            
        # Set loading state immediately
        self.update_status("Starting search...")
        self._set_buttons_loading_state(True)
        
        # Start processing in background thread
        thread = threading.Thread(target=self._find_busy_place_threaded, daemon=True)
        thread.start()

    def find_idle_place(self):
        # Prevent multiple simultaneous executions
        if self.is_processing:
            return
            
        # Set loading state immediately
        self.update_status("Starting search...")
        self._set_buttons_loading_state(True)
        
        # Start processing in background thread
        thread = threading.Thread(target=self._find_idle_place_threaded, daemon=True)
        thread.start()

    def add_route_event(self, coords):
        """
        Handle right-click menu "Route to here" command on the map.
        
        Creates a route from the current location to the coordinates where the user
        right-clicked on the map. Clears existing markers and paths, then displays
        the new route with driving directions, distance, and duration information.
        
        Args:
            coords (tuple): Target coordinates as (latitude, longitude) from map right-click
        
        Returns:
            None
        
        Side Effects:
            - Prints "Add marker:" message with coordinates to console
            - Clears all existing markers and paths from the map
            - Adds marker for current location if available
            - Sets new marker at target coordinates with blue styling
            - Calculates and displays driving route using OSRM
            - Updates route label with distance and duration information
            - Prints route generation and coordinate information to console
        
        UI Updates:
            - Map markers: current location (default style) + target (blue)
            - Map path: driving route with multiple waypoints
            - Route label: "Current Route:\n\nDistance: X km\nDuration: Y minutes"
        
        Map Integration:
            - Triggered by right-click context menu on map widget
            - Coordinates are automatically passed by tkintermapview
            - Menu item added in __init__ with pass_coords=True
        
        Notes:
            - Requires self.current_location_coords to be set for route calculation
            - Uses get_driving_route_with_osrm() for realistic driving directions
            - Provides interactive way for users to explore routes to any map location
            - Marker styling matches other route destination markers in the app
        
        Example:
            >>> # User right-clicks on map at Amsterdam coordinates
            >>> # This method is automatically called with coords=(52.3676, 4.9041)
            Add marker: (52.3676, 4.9041)
            Generated driving route with 89 waypoints
            Setting route to coordinates: 52.3676, 4.9041
        """
        print("Add marker:", coords)
        self.map_widget.delete_all_marker()
        if self.current_location_coords:
            self.map_widget.set_marker(self.current_location_coords[0], self.current_location_coords[1])
        self.map_widget.delete_all_path()

        lat, lon = coords
        new_area_marker = self.map_widget.set_marker(lat, lon, marker_color_circle="dodgerblue4", marker_color_outside="steelblue")

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
import tkinter as tk
from tkintermapview import TkinterMapView
from tkinter import ttk

class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Uber Driver Assistant")
        self.window.geometry("1200x800")

        # Create main frame with grid layout
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create left panel for controls
        control_panel = tk.Frame(main_frame, width=250, bg='lightgray')
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_panel.pack_propagate(False)

        # Create right panel for map
        map_frame = tk.Frame(main_frame)
        map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add title to control panel
        title_label = tk.Label(control_panel, text="Uber Driver Assistant", 
                              font=('Arial', 16, 'bold'), bg='lightgray')
        title_label.pack(pady=10)

        # Add map controls
        self.setup_map_controls(control_panel)

        # Create the map view
        self.map_widget = TkinterMapView(map_frame, width=900, height=700, corner_radius=0)
        self.map_widget.pack(fill=tk.BOTH, expand=True)

        # Set initial map position (San Francisco as example)
        self.map_widget.set_position(37.7749, -122.4194)  # San Francisco coordinates
        self.map_widget.set_zoom(13)

        # Add a marker for current location
        self.current_location_marker = self.map_widget.set_marker(37.7749, -122.4194, 
                                                                 text="Current Location")

        # Start the event loop.
        self.window.mainloop()

    def setup_map_controls(self, parent):
        """Setup map control buttons and information in the control panel"""
        
        # Location input section
        location_frame = tk.LabelFrame(parent, text="Location Search", bg='lightgray')
        location_frame.pack(fill=tk.X, padx=10, pady=5)

        self.location_entry = tk.Entry(location_frame, width=25)
        self.location_entry.pack(pady=5)
        self.location_entry.insert(0, "Enter location...")

        search_button = tk.Button(location_frame, text="Search Location", 
                                 command=self.search_location)
        search_button.pack(pady=5)

        # Map controls section
        controls_frame = tk.LabelFrame(parent, text="Map Controls", bg='lightgray')
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # Zoom controls
        zoom_in_button = tk.Button(controls_frame, text="Zoom In", 
                                  command=self.zoom_in)
        zoom_in_button.pack(side=tk.LEFT, padx=2, pady=5)

        zoom_out_button = tk.Button(controls_frame, text="Zoom Out", 
                                   command=self.zoom_out)
        zoom_out_button.pack(side=tk.LEFT, padx=2, pady=5)

        # Reset view button
        reset_button = tk.Button(controls_frame, text="Reset View", 
                                command=self.reset_view)
        reset_button.pack(side=tk.LEFT, padx=2, pady=5)

        # Driver information section
        info_frame = tk.LabelFrame(parent, text="Driver Info", bg='lightgray')
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = tk.Label(info_frame, text="Status: Available", 
                                    bg='lightgray', font=('Arial', 10, 'bold'))
        self.status_label.pack(pady=5)

        self.location_label = tk.Label(info_frame, text="Location: San Francisco, CA", 
                                      bg='lightgray', wraplength=200)
        self.location_label.pack(pady=5)

        # Close button
        close_button = tk.Button(parent, text="Close App", 
                                command=self.window.destroy,
                                bg='red', fg='white', font=('Arial', 10, 'bold'))
        close_button.pack(side=tk.BOTTOM, pady=10)

    def search_location(self):
        """Search for a location and center the map on it"""
        location = self.location_entry.get()
        if location and location != "Enter location...":
            try:
                # This will search for the location and center the map
                self.map_widget.set_address(location)
                # Update location label
                self.location_label.config(text=f"Location: {location}")
            except Exception as e:
                print(f"Error searching location: {e}")

    def zoom_in(self):
        """Zoom in the map"""
        current_zoom = self.map_widget.get_zoom()
        self.map_widget.set_zoom(current_zoom + 1)

    def zoom_out(self):
        """Zoom out the map"""
        current_zoom = self.map_widget.get_zoom()
        self.map_widget.set_zoom(current_zoom - 1)

    def reset_view(self):
        """Reset map to default view"""
        self.map_widget.set_position(37.7749, -122.4194)
        self.map_widget.set_zoom(13)
        self.location_label.config(text="Location: San Francisco, CA")
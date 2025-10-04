from datetime import datetime

def get_venue_type():
    now = datetime.now()
    current_hour = now.hour
    current_weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    venue_types = []
    
    if 12 <= current_hour <= 14:
        venue_types.append("Cafés")
    
    if 19 <= current_hour <= 22:
        venue_types.append("Restaurants")
    
    if (22 <= current_hour <= 23) or (2 <= current_hour <= 5):
        venue_types.append("Clubs")
    
    airport_base_hours = (4 <= current_hour <= 8) or (21 <= current_hour <= 23)
    sunday_evening = (current_weekday == 6 and current_hour >= 18)  # Sunday evening
    monday_morning = (current_weekday == 0 and current_hour < 12)   # Monday morning
    
    if airport_base_hours or sunday_evening or monday_morning:
        venue_types.append("Airports")
    
    if (7 <= current_hour <= 10) or (15 <= current_hour <= 18):
        venue_types.append("Hotels")
    
    if 11 <= current_hour <= 16:
        venue_types.append("Parks")

    if 6 <= current_hour <= 9:
        venue_types.append("Transportation Hubs")
    
    if (16 <= current_hour <= 20) and (0 <= current_weekday <= 4):
        venue_types.append("Offices")

    return venue_types if venue_types else ["No venues open at this time"]


# Example usage and testing function
def test_venue_chooser():
    """Test function to demonstrate the venue chooser"""
    current_venue = get_venue_type()
    current_time = datetime.now().strftime("%H:%M on %A")
    print(f"Current time: {current_time}")
    print(f"Recommended venue type: {current_venue}")


if __name__ == "__main__":
    test_venue_chooser()


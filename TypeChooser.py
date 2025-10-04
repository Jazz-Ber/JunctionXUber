from datetime import datetime
import csv
from Services.CSVService import Id_To_Name
from Services.parsers import Parsers

parsers = Parsers()

def get_venue_type():
    now = datetime.now()
    current_hour = now.hour
    current_weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    venue_types = []

    import os
    csv_file_path = os.path.join(os.path.dirname(__file__), "Data", "taxi_demand_categories_explicit.csv")
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            start_time = parsers.Parse_Time_String(row['Start Time'].strip().strip('"').strip("'"))
            end_time = parsers.Parse_Time_String(row['End Time'].strip().strip('"').strip("'"))
            valid_days = parsers.Parse_Day_String(row['Days'])
            
            if current_weekday in valid_days:
                if start_time > end_time:
                    if current_hour >= start_time.hour or current_hour <= end_time.hour:
                        venue_types.append(row['Category ID'])
                elif start_time.hour <= current_hour <= end_time.hour:
                    venue_types.append(row['Category ID'])
        
    return venue_types if venue_types else ["No venues open at this time"]
    
    

# Example usage and testing function
def test_venue_chooser():
    """Test function to demonstrate the venue chooser"""
    current_venue = get_venue_type()
    print(datetime.now())
    for venue in current_venue:
        print(venue + Id_To_Name(venue))


if __name__ == "__main__":
    test_venue_chooser()


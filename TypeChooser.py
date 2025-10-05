from datetime import datetime
import csv
import os
from Services.parsers import parse_time_string, parse_day_string

def get_venue_type():
    """
    Retrieves the types of venues which would theoretically be busy in the current hours and days. The returned list is a list of Category IDs
    """
    now = datetime.now()
    current_hour = now.hour
    current_weekday = now.weekday()
    venue_types = []

    csv_file_path = os.path.join(os.path.dirname(__file__), "Data", "taxi_demand_categories_explicit.csv")
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            start_time = parse_time_string(row['Start Time'].strip().strip('"').strip("'"))
            end_time = parse_time_string(row['End Time'].strip().strip('"').strip("'"))
            valid_days = parse_day_string(row['Days'])
            
            if current_weekday in valid_days:
                if start_time > end_time:
                    if current_hour >= start_time.hour or current_hour <= end_time.hour:
                        venue_types.append(row['Category ID'])
                elif start_time.hour <= current_hour <= end_time.hour:
                    venue_types.append(row['Category ID'])
        
    return venue_types if venue_types else ["No venues open at this time"]    

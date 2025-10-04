from datetime import datetime
import csv
from Services.CSVService import Id_To_Name
from Services.parsers import Parsers

parsers = Parsers()

def get_venue_type():
    """
    Determines which venue types are currently open based on the current time and day.

    This function reads from a CSV file containing venue category information, including
    their operating hours and valid days. It checks the current system time and day,
    and returns a list of category IDs for venues that are open at the moment.

    Returns:
        list: A list of 'Category ID' strings for venues currently open.
              If no venues are open, returns ["No venues open at this time"].

    CSV File Format (taxi_demand_categories_explicit.csv):
        - 'Category ID': Unique identifier for the venue type.
        - 'Start Time': Opening time (string, e.g., "18:00").
        - 'End Time': Closing time (string, e.g., "02:00").
        - 'Days': Comma-separated days or ranges (e.g., "Mon-Fri,Sat").

    Notes:
        - Handles venues that are open overnight (e.g., 18:00 to 02:00).
        - Uses helper methods from the Parsers class to parse time and day strings.
        - Weekdays are represented as integers: 0=Monday, 6=Sunday.

    Example:
        >>> get_venue_type()
        ['1001', '1002']

    """
    now = datetime.now()
    current_hour = now.hour
    current_weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    venue_types = []

    csv_file_path = "Data/taxi_demand_categories_explicit.csv"
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


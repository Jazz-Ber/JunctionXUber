import csv

"This class is mostly used for debugging with printing"

def id_to_name(search_term=""):
    """
    Finds the name of a category by searching by its ID
    """
    csv_file_path = "Data/personalization-apis-movement-sdk-categories.csv"

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Category ID'] == search_term:
                return row['Category Name']
    return None

def name_to_id(search_term=""):
    """
    Finds an ID of a category by searching by its name
    """
    csv_file_path = "Data/personalization-apis-movement-sdk-categories.csv"
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Category Name'] == search_term:
                return row['Category ID']
    return None
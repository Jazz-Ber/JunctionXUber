import csv

def Id_To_Name(search_term=""):
    csv_file_path = "Data/personalization-apis-movement-sdk-categories.csv"

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Category ID'] == search_term:
                return row['Category Name']
    return None

def Name_To_Id(search_term=""):
    csv_file_path = "Data/personalization-apis-movement-sdk-categories.csv"
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Category Name'] == search_term:
                return row['Category ID']
    return None
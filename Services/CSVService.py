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


def Name_To_IdTest():
    print(Name_To_Id("Escape Room"))

def Id_To_NameTest():
    print(Id_To_Name("5f2c2834b6d05514c704451e"))


if __name__ == "__main__":
    Id_To_NameTest()
    Name_To_IdTest()

from datetime import datetime

class Parsers():

    @staticmethod
    def Parse_Time_String(time_string):
        if time_string == "24:00":
            return datetime.strptime("00:00", "%H:%M").time()
        return datetime.strptime(time_string, "%H:%M").time()

    @staticmethod
    def Parse_Day_String(day_string):
        day_mapping = {
            'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 
            'Fri': 4, 'Sat': 5, 'Sun': 6
        }
        
        if '-' in day_string:
            start_day, end_day = day_string.split('-')
            start_num = day_mapping.get(start_day)
            end_num = day_mapping.get(end_day)
            
            if start_num is not None and end_num is not None:
                if start_num > end_num:
                    return list(range(start_num, 7)) + list(range(0, end_num))
                else:
                    return list(range(start_num, end_num))
        
        return []
            
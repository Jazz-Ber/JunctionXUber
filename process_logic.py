import geopy.distance
from ui import geocode_address

class ProcessLogic:
    def __init__(self):
        # Cache for geocoded addresses to avoid repeated API calls
        self.geocoding_cache = {}
    
    def geocode_address_cached(self, address):
        """Geocode an address with caching to avoid repeated API calls"""
        if address not in self.geocoding_cache:
            self.geocoding_cache[address] = geocode_address(address)
        return self.geocoding_cache[address]
    
    def distance_finder(self, coords1, coords2):
        """Calculate distance between two coordinate tuples"""
        return round(geopy.distance.geodesic(coords1, coords2).km, 3)

    def distance_to_coords_finder(self, coords1, coords2):
        """Calculate distance between two coordinate tuples"""
        return round(geopy.distance.geodesic(coords1, coords2).km, 3)

    def cluster_average(self, cluster_coords):
        """Calculate average coordinates from a list of coordinate tuples"""
        if not cluster_coords:
            return None
        
        lat = [coord[0] for coord in cluster_coords if coord is not None]
        long = [coord[1] for coord in cluster_coords if coord is not None]
        
        if not lat or not long:
            return None
            
        return sum(lat) / len(lat), sum(long) / len(long)

    def cluster_merger(self, clusters, cluster_difference, index):
        if(len(clusters) <=1 or cluster_difference <= 0 or index >= len(clusters)):
            return None
        changed = False
        untouched_clusters = clusters.copy()
        new_clusters = []

        current_cluster = untouched_clusters.pop(index)
        for i in range(len(untouched_clusters) - 1, -1, -1):
            if (round(geopy.distance.geodesic(current_cluster[1], untouched_clusters[i][1]).km, 3) <= 2 * cluster_difference):
                added_cluster = untouched_clusters.pop(i)

                cluster_1_len = len(current_cluster[0])
                cluster_2_len = len(added_cluster[0])

                new_average_lan = (current_cluster[1][0] * cluster_1_len + added_cluster[1][0] * cluster_2_len) / (cluster_1_len + cluster_2_len)
                new_average_long = (current_cluster[1][1] * cluster_1_len + added_cluster[1][1] * cluster_2_len) / (cluster_1_len + cluster_2_len)

                current_cluster = (current_cluster[0] + added_cluster[0], (new_average_lan, new_average_long))
                changed = True

        if not changed:
            return None

        new_clusters.append(current_cluster)
        if untouched_clusters:
            for i in untouched_clusters:
                new_clusters.append(i)
        return new_clusters
        


    def cluster_maker(self, places):
        """Optimized clustering algorithm that geocodes all addresses once at the beginning"""
        if not places:
            return []
        
        # Step 1: Geocode all addresses once and create address->coords mapping
        address_coords_map = {}
        valid_places = []
        
        for address in places:
            coords = self.geocode_address_cached(address)
            if coords is not None:
                address_coords_map[address] = coords
                valid_places.append(address)
            else:
                print(f"Warning: Could not geocode address: {address}")
        
        if not valid_places:
            return []
        
        
        # Step 2: Convert to coordinate-based clustering
        untouched_coords = [(address, address_coords_map[address]) for address in valid_places]
        clusters = []
        cluster_difference = 1

        # Step 3: Initial clustering based on coordinates
        while len(untouched_coords) != 0:
            current_item = untouched_coords.pop()
            current_address, current_coords = current_item
            single_cluster = [current_item]
            cluster_center = current_coords
            
            for i in range(len(untouched_coords) - 1, -1, -1):
                _, coords = untouched_coords[i]
                if self.distance_to_coords_finder(cluster_center, coords) <= cluster_difference:
                    single_cluster.append(untouched_coords.pop(i))
                    # Update cluster center to average of all addresses in cluster
                    cluster_center = self.cluster_average([item[1] for item in single_cluster])

            clusters.append(single_cluster)

        # Step 4: Convert to final format with addresses and average coordinates
        final_clusters = []
        for cluster in clusters:
            addresses = [item[0] for item in cluster]
            avg_coords = self.cluster_average([item[1] for item in cluster])
            final_clusters.append((addresses, avg_coords))

        # Step 5: Merge nearby clusters
        index = 0
        while(True):
            result = self.cluster_merger(final_clusters, cluster_difference, index)
            if result is None:
                index += 1
                if(index >= len(final_clusters)):
                    break
                continue
            else:
                final_clusters = result
                continue

        return final_clusters


locations_delft = ["Brabantse Turfmarkt 67, 2611 CM Delft", "Voldersgracht 7, 2611 ET Delft", "Oude Delft 92, 2611 CE Delft", 
                    "Choorstraat 24, 2611 JG Delft", "Beestenmarkt 5, 2611 GA Delft", "Phoenixstraat 4C, 2611 AL Delft", 
                    "Kromstraat 29, 2611 EP Delft", "Vlamingstraat 2, 2611 KW Delft", "Markt 69, 2611 GS Delft"]

locations_denhaag = ["Raamstraat 15, 2512 BX Den Haag", "Korte Houtstraat 5, 2511 CC Den Haag", "Oude Molstraat 21, 2513 BA Den Haag", 
                    "Lutherse Burgwal 5, 2512 CB Den Haag", "Papestraat 30, 2513 AW Den Haag", "Prinsestraat 124, 2513 CH Den Haag", 
                    "Oude Molstraat 13, 2513 BA Den Haag", "Riviervismarkt 1, 2513 AM Den Haag", "Grote Markt 29, 2511 BG Den Haag"]

locations = locations_delft + locations_denhaag

processor = ProcessLogic()
result = processor.cluster_maker(locations)

print(result)
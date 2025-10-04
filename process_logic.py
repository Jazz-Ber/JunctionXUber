import geopy.distance
import requests

class ProcessLogic:
    
    def distance_finder(self, coords1, coords2):
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
            if (self.distance_finder(current_cluster[1], untouched_clusters[i][1]) <= 2 * cluster_difference):
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
        
        # Convert to coordinate-based clustering
        untouched_coords = places.copy()
        clusters = []
        cluster_difference = 1

        # Initial clustering based on coordinates
        while len(untouched_coords) != 0:
            current_item = untouched_coords.pop()
            single_cluster = [current_item]
            cluster_center = current_item
            
            for i in range(len(untouched_coords) - 1, -1, -1):
                coords = untouched_coords[i]
                if self.distance_finder(cluster_center, coords) <= cluster_difference:
                    single_cluster.append(untouched_coords.pop(i))
                    # Update cluster center to average of all addresses in cluster
                    cluster_center = self.cluster_average(single_cluster)

            clusters.append((single_cluster, cluster_center))

        # Merge nearby clusters
        index = 0
        while(True):
            result = self.cluster_merger(clusters, cluster_difference, index)
            if result is None:
                index += 1
                if(index >= len(clusters)):
                    break
                continue
            else:
                clusters = result
                continue

        return clusters
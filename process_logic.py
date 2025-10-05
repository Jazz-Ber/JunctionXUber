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
        """
        Merge clusters that are within a specified distance threshold.

        This method attempts to merge the cluster at the given `index` in the `clusters` list
        with any other clusters whose centers are within twice the `cluster_difference` distance.
        The merging process combines the points of the clusters and recalculates the new cluster center
        as a weighted average based on the number of points in each cluster.

        Args:
            clusters (list): A list of clusters, where each cluster is a tuple:
                             ([list of (lat, lon) tuples in cluster], (average_lat, average_lon) of cluster)
            cluster_difference (float): The distance threshold (in kilometers) for merging clusters.
            index (int): The index of the cluster in `clusters` to attempt to merge with others.

        Returns:
            list or None: 
                - If a merge occurs, returns a new list of clusters with the merged cluster and remaining clusters.
                - If no merge occurs, returns None.

        Notes:
            - Only clusters whose centers are within 2 * cluster_difference are merged.
            - The merged cluster's center is recalculated as a weighted average of the original centers.
            - If no clusters are merged, the method returns None.
            - The input list `clusters` is not modified; a copy is used internally.

        Example:
            >>> clusters = [
            ...     ([(52.01, 4.36)], (52.01, 4.36)),
            ...     ([(52.02, 4.37)], (52.02, 4.37)),
            ...     ([(52.20, 4.50)], (52.20, 4.50))
            ... ]
            >>> result = process_logic.cluster_merger(clusters, 1, 0)
            >>> print(result)
            # Output: merged clusters if within threshold, else None
        """
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
        """
        Cluster a list of coordinate tuples into spatial groups based on proximity.

        This method performs spatial clustering on a list of places, where each place is
        represented as a (latitude, longitude) tuple. It groups together locations that are
        within a specified distance threshold (1 km by default) of each other. The algorithm
        works in two main phases:

        1. **Initial Clustering**: Iteratively builds clusters by grouping together all points
           within the distance threshold of the current cluster center. The cluster center is
           updated as the average of all points in the cluster as new points are added.

        2. **Cluster Merging**: After initial clusters are formed, the method attempts to merge
           clusters whose centers are within twice the distance threshold of each other, to
           avoid fragmented clusters.

        Args:
            places (list of tuple): A list of (latitude, longitude) coordinate tuples to cluster.

        Returns:
            list: A list of clusters, where each cluster is a tuple:
                  ([list of (lat, lon) tuples in cluster], (average_lat, average_lon) of cluster)

        Example:
            >>> places = [(52.01, 4.36), (52.02, 4.37), (52.20, 4.50)]
            >>> clusters = process_logic.cluster_maker(places)
            >>> for cluster in clusters:
            ...     print(cluster)
            ([(52.02, 4.37), (52.01, 4.36)], (52.015, 4.365))
            ([(52.2, 4.5)], (52.2, 4.5))

        Notes:
            - The distance threshold for clustering is set to 1 km.
            - The method assumes all input places are valid (lat, lon) tuples.
            - The method does not perform geocoding; input must be coordinates.
            - The returned clusters can be used for further analysis, such as finding the
              busiest or most idle area.

        """
        if not places:
            return []
        
        # Convert to coordinate-based clustering
        untouched_coords = places.copy()
        clusters = []
        cluster_difference = 1.5

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
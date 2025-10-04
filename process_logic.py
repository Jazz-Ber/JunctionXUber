import geopy.distance
from ui import geocode_address

class ProcessLogic:
    def distance_finder(address1, address2):
        coords1 = geocode_address(address1)
        coords2 = geocode_address(address2)

        return round(geopy.distance.geodesic(coords1, coords2).km, 3)

    def distance_to_coords_finder(coords, address):
        coords2 = geocode_address(address)

        return round(geopy.distance.geodesic(coords, coords2).km, 3)

    def cluster_average(cluster):
        lat = []
        long = []

        for i in cluster:
            coords = geocode_address(i)
            if coords is not None:
                lat.append(coords[0])
                long.append(coords[1])

        return sum(lat) / len(lat), sum(long) / len(long)

    def cluster_merger(clusters, cluster_difference, index):
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
        


    def cluster_maker(places):
        untouched_places = places.copy()
        clusters = []

        cluster_difference = 1

        while len(untouched_places) != 0:
            current_address = untouched_places.pop()
            single_cluster = [current_address]
            cluster_average = geocode_address(current_address)
            for i in range(len(untouched_places) - 1, -1, -1):
                if ProcessLogic.distance_to_coords_finder(cluster_average, untouched_places[i]) <= cluster_difference:
                    single_cluster.append(untouched_places.pop(i))
                    cluster_average = ProcessLogic.cluster_average(single_cluster)

            clusters.append(single_cluster)

        for i in range(len(clusters)):
            clusters[i] = (clusters[i], ProcessLogic.cluster_average(clusters[i]))

        index = 0
        while(True):
            result = ProcessLogic.cluster_merger(clusters, cluster_difference, index)
            if result is None:
                index += 1
                if(index >= len(clusters)):
                    break
                continue
            else:
                clusters = result
                continue

        return clusters
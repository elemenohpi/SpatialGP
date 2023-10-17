from sklearn.cluster import DBSCAN
import numpy as np

# List of coordinates in the format (x, y)
coordinates = [(1, 1), (2, 1), (-6, 7), (-7, 7)]

# Convert coordinates to a NumPy array for easier manipulation
coords_array = np.array(coordinates)

# Define the epsilon (maximum distance between two samples for one to be considered as in the neighborhood of the other) and minimum_samples parameters for DBSCAN
epsilon = 2  # Radius of the circle
min_samples = 2  # Minimum number of points in a cluster

# Create a DBSCAN clusterer
dbscan = DBSCAN(eps=epsilon, min_samples=min_samples)

# Fit the clusterer to the data
dbscan.fit(coords_array)

# Extract cluster labels
labels = dbscan.labels_
print(labels)

# Create a dictionary to group coordinates by their cluster label
clustered_coordinates = {}
for label, coord in zip(labels, coordinates):
    if label in clustered_coordinates:
        clustered_coordinates[label].append(coord)
    else:
        clustered_coordinates[label] = [coord]

# Print the coordinates in each cluster
for label, cluster in clustered_coordinates.items():
    print(f"Cluster {label}: {cluster}")
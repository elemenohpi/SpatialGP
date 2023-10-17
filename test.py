import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_points(points, r):
    # Extract x and y values
    x_vals = [p[0] for p in points]
    y_vals = [p[1] for p in points]

    # Create the KDE plot with reduced bandwidth
    plt.figure(figsize=(10, 10))
    sns.kdeplot(x=x_vals, y=y_vals, cmap="Reds", fill=True, bw_method=0.2, levels=100)

    # Plot the circle to visualize the boundary
    circle = plt.Circle((0, 0), r, color='black', fill=False)
    plt.gca().add_patch(circle)

    # Add x and y axis
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)

    # Set the aspect of the plot to be equal, so the circle isn't elliptical
    plt.gca().set_aspect('equal', adjustable='box')

    # Adjust the x and y limits to ensure the entire circle is visible
    plt.xlim([-r-1, r+1])
    plt.ylim([-r-1, r+1])

    # Display the plot
    plt.show()

# Sample data
points = [
    (1, 2), (2, 1), (3, 3), (-1, -2), (-2, -1),
    (-3, -3), (1, -2), (-1, 2), (-2.5, 2.5), (2.5, -2.5)
]
r = 5
visualize_points(points, r)

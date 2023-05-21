import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle


def create_evo_plot(file_path, output_path):
    # Read the data from the file
    df = pd.read_csv(file_path)

    # Plotting the line plot
    fig, ax = plt.subplots()
    ax.plot(df["gen"], df["best"], label="Best")
    ax.plot(df["gen"], df["avg"], label="Average")

    # Set plot labels and legend
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.set_title("Evolution Plot")
    ax.legend()

    # Display the plot
    plt.savefig(output_path)
    plt.close()


def create_heatmap(coordinates, file_path, radius):
    # Extract x and y coordinates from the input list
    x = [coord[0] for coord in coordinates]
    y = [coord[1] for coord in coordinates]

    # Define the grid for the heatmap
    grid_size = 100  # Adjust this value to control the resolution of the heatmap
    x_range = np.linspace(min(x) - radius, max(x) + radius, grid_size)
    y_range = np.linspace(min(y) - radius, max(y) + radius, grid_size)
    xx, yy = np.meshgrid(x_range, y_range)

    # Create the heatmap using the interpolated values
    heatmap = np.zeros((grid_size, grid_size))
    for coord in coordinates:
        heatmap += np.exp(-((xx - coord[0]) ** 2 + (yy - coord[1]) ** 2))

    # Plot the heatmap
    plt.imshow(heatmap, extent=(x_range.min(), x_range.max(), y_range.min(), y_range.max()), origin='lower',
               cmap='hot')
    plt.colorbar()

    # Plot the circle
    circle = Circle((0, 0), radius, edgecolor='white', facecolor='none')
    plt.gca().add_patch(circle)

    # Add x and y axes
    plt.axhline(0, color='blue', linestyle='--', linewidth=0.5)
    plt.axvline(0, color='blue', linestyle='--', linewidth=0.5)

    # Set plot labels and title
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Heatmap')

    # Save the plot as an image file
    plt.savefig(file_path)
    plt.close()



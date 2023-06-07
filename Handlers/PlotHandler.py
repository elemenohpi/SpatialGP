import os

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle


def create_evo_plots(file_path, output_path):
    # Read the data from the file
    df = pd.read_csv(file_path)

    # Plotting the line plot
    fig, ax = plt.subplots()
    ax.plot(df["gen"], df["best"], label="Best")
    # ax.plot(df["gen"], df["avg"], label="Average")
    # Set plot labels and legend
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.set_title("Fitness over generation for the best individual")
    ax.legend()

    # Display the plot
    plt.savefig(output_path + "best_plot.png")
    plt.close()

    fig, ax = plt.subplots()
    ax.plot(df["gen"], df["avg"], label="Average")
    # Set plot labels and legend
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.set_title("Fitness over generation for the average population")
    ax.legend()

    # Display the plot
    plt.savefig(output_path + "avg_plot.png")


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
    plt.title('Spatial heatmap of the population')

    # Save the plot as an image file
    plt.savefig(file_path)
    plt.close()


def get_avg_dataframe(path_to_files):
    files = [file for file in os.listdir(path_to_files) if file.endswith('.csv')]
    dfs = []
    for file in files:
        file_path = os.path.join(path_to_files, file)
        df = pd.read_csv(file_path)
        dfs.append(df)

    combined_df = pd.concat(dfs)
    average_best = combined_df.groupby('gen')['best'].mean().reset_index()

    return average_best


def compare_experiments(path, key=None):
    directories = list_directories(path, key)
    plot_data = []
    for directory in directories:
        avg_dataframe = get_avg_dataframe(os.path.join(path, directory, "Evo"))
        directory_data = [directory, avg_dataframe]
        plot_data.append(directory_data)

    # Plotting the line plot
    fig, ax = plt.subplots()
    for directory_data in plot_data:
        ax.plot(directory_data[1]["gen"], directory_data[1]["best"], label=directory_data[0])

    # Set plot labels and legend
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.set_title("Fitness over generation for the best individual")
    ax.legend()

    # Display the plot
    plt.show()
    plt.close()


def list_directories(path, key):
    directories = []
    for entry in os.listdir(path):
        if os.path.isdir(os.path.join(path, entry)):
            directories.append(entry)
    parsed_directories = []
    for directory in directories:
        if key is not None:
            if key not in directory:
                continue
        parsed_directories.append(directory)
    return parsed_directories


if __name__ == "__main__":
    equation = "E9"
    compare_experiments(f"../HPCC Experiments/{equation}", f"{equation}Ablation")
    # compare_experiments(f"../HPCC Experiments/{equation}", f"{equation}Ablation_{equation}_mutation")
    # compare_experiments(f"../HPCC Experiments/{equation}", f"{equation}Ablation_{equation}_nonspatial_mutation")
    # compare_experiments(f"../HPCC Experiments/{equation}", f"{equation}Ablation_{equation}_spatial_mutation")
    # compare_experiments(f"../HPCC Experiments/{equation}", "nocrossover")
    compare_experiments(f"../HPCC Experiments/{equation}", "high_LGP")
    compare_experiments(f"../HPCC Experiments/{equation}", "retcon")

    pass

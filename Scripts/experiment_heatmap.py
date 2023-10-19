import os
import pickle

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
import seaborn as sns


def create_heatmap(points, file_path, r):
    # Extract x and y values
    x_vals = [p[0] for p in points]
    y_vals = [p[1] for p in points]
    # Create the KDE plot with reduced bandwidth
    plt.figure(figsize=(10, 10))
    sns.kdeplot(x=x_vals, y=y_vals, cmap="Reds", fill=True, bw_method=0.05, levels=100)

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
    plt.title('Spatial heatmap of the population')
    #
    # Save the plot as an image file
    if not file_path:
        plt.show()
    else:
        plt.savefig(file_path)
    plt.close()


def get_pop_coordinates(path):
    coord_list = []
    with open(path, "rb") as file:
        pop_obj = pickle.load(file)
    for indv in pop_obj.pop:
        for program in indv.programs:
            coord_list.append(program.pos)
    return coord_list


def analyze_run(path):
    pop_path = os.path.join(path, "Population")
    pop_files = os.listdir(pop_path)
    run_coordinates = []
    for pop_file in pop_files:
        run_coordinates += get_pop_coordinates(os.path.join(pop_path, pop_file, "pop.sgp"))
    return run_coordinates


def extract_quadrant_data(run_data):
    data = [0] * 4
    for point in run_data:
        if point[0] >= 0 and point[1] >= 0:
            # pos pos Q1
            data[0] += 1
        elif point[0] >= 0 and point[1] < 0:
            # pos neg Q2
            data[1] += 1
        elif point[0] < 0 and point[1] < 0:
            # neg neg Q3
            data[2] += 1
        elif point[0] < 0 and point[1] >= 0:
            # neg pos Q4
            data[3] += 1

    return data


def analyze_experiment(path, out_path):
    run_directory_names = os.listdir(path)
    experiment_data = []
    for directory_name in run_directory_names:
        # Pre-process or skip files here <<
        # if "m_60" not in directory_name:
        #     print(directory_name)
        #     continue
        print(f"Working on {directory_name}")

        run_data = analyze_run(os.path.join(path, directory_name))
        experiment_data.append(run_data)
        quadrant_data = extract_quadrant_data(run_data)
        print(f"Q1 {quadrant_data[0]} Q2 {quadrant_data[1]} Q3 {quadrant_data[2]} Q4 {quadrant_data[3]}")
        create_heatmap(run_data, out_path, 150)


if __name__ == "__main__":
    exp_path = "../../HPCC_Experiments/SpatialOp"
    analyze_experiment(exp_path, None)


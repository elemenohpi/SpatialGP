import os

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker
from matplotlib.patches import Circle
from scipy import stats


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

    # formatter = ticker.ScalarFormatter(useMathText=True)
    # formatter.set_scientific(True)
    # # formatter.set_powerlimits((-3, 3))
    #
    # # Apply the formatter to the y-axis
    # plt.gca().yaxis.set_major_formatter(formatter)

    # Set the desired number of ticks on the y-axis
    num_ticks = 10
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(num_ticks))

    # Display the plot
    plt.savefig(output_path + "avg_plot.png")
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
    circle = Circle((0, 0), radius, edgecolor='blue', facecolor='none')
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


def get_avg_dataframe(path_to_files, max_gen):
    files = [file for file in os.listdir(path_to_files) if file.endswith('.csv')]
    dfs = []
    for file in files:
        file_path = os.path.join(path_to_files, file)
        df = pd.read_csv(file_path)
        df = df.apply(pd.to_numeric, errors='coerce')

        dfs.append(df)

    combined_df = pd.concat(dfs)
    average_best = combined_df.groupby('gen')['best'].median().reset_index()
    average_best = average_best[:max_gen]

    # Calculate confidence interval
    confidence_interval = []
    all_percentiles = []
    for gen in average_best['gen']:
        values = np.array(combined_df[combined_df['gen'] == gen]['best'])
        n = len(values)  # Sample size
        mean = np.mean(values)  # Sample mean
        sem = stats.sem(values)  # Standard error of the mean
        ci = stats.t.interval(0.95, n - 1, loc=mean, scale=sem)  # Calculate confidence interval
        confidence_interval.append(ci)
        percentiles = [25, 75]
        percentile_values = np.percentile(values, percentiles)
        all_percentiles.append(percentile_values)

    average_best['confidence_interval'] = confidence_interval
    average_best['percentiles'] = all_percentiles
    return average_best


def compare_experiments(path, n=100, key=None):
    directories = list_directories(path, key)
    plot_data = []
    for directory in directories:
        if "clusters" in directory:
            continue
        median_dataframe = get_avg_dataframe(os.path.join(path, directory, "Evo"), n)
        directory_data = [directory, median_dataframe]
        plot_data.append(directory_data)

    # Plotting the line plot
    fig, ax = plt.subplots()
    colors = ["blue", "red", "green", "brown", "purple", "yellow", "cyan", "orange", "pink", "Black", "lime", "Gray",
              "crimson", "lavender", "indigo", "teal", "maroon", "fuchsia", "azure", "teal"]
    # labels = ["LGP", "SGP sm20", "SGP sm40", "SGP sm60"]
    for index, directory_data in enumerate(plot_data):
        gen_data = directory_data[1]["gen"]
        median_best = np.array(directory_data[1]["best"])
        confidence_interval = np.array(directory_data[1]["confidence_interval"])
        lower_bound, upper_bound = zip(*confidence_interval)
        percentiles = directory_data[1]["percentiles"]
        lower, upper = zip(*percentiles)

        ax.plot(gen_data, median_best, label=directory_data[0])
        # ax.errorbar(gen_data, median_best, yerr=[median_best - lower_bound, upper_bound -
        #                                          median_best], fmt='.', capsize=4)
        plt.fill_between(gen_data, lower, upper, color=colors[index],
                         alpha=0.1)

    # Set plot labels and legend
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness (RMSE)")
    ax.set_title("Fitness over generation for the best individuals")
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
    # equation = "E9"
    # compare_experiments(f"../HPCC Experiments/{equation}", f"{equation}Ablation")
    # compare_experiments(f"../HPCC Experiments/{equation}", f"{equation}Ablation_{equation}_mutation")
    # compare_experiments(f"../HPCC Experiments/{equation}", f"{equation}Ablation_{equation}_nonspatial_mutation")
    # compare_experiments(f"../HPCC Experiments/{equation}", f"{equation}Ablation_{equation}_spatial_mutation")
    # compare_experiments(f"../HPCC Experiments/{equation}", "nocrossover")
    # compare_experiments(f"../HPCC Experiments/{equation}", "high_LGP")
    # compare_experiments(f"../HPCC Experiments/{equation}", "retcon")
    # compare_experiments(f"../../Results/F6/", 100, "TGP6_II242")
    # compare_experiments(f"../../Results/F6/", 100, "Feynman6_II242")
    # compare_experiments(f"../../Results/F6/", 100, "F6LGP_II242")
    # compare_experiments(f"../../Results/F6/", 100, "F")
    compare_experiments(f"../../HPCC_Experiments/Localization", 99, "")
    # compare_experiments(f"../../Results/F1-4/F1-4Res/", 100, "Feynman1")
    pass

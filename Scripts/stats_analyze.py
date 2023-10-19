import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def analyze_stats(path):
    if not os.path.exists(path):
        raise ValueError(f"The provided path does not exist: {path}")
    with open(path, "r") as file:
        lines = file.readlines()
    counts = []
    for line in lines:
        number_of_statements_per_gen = line.replace(" ", "").split(",")
        if "" in number_of_statements_per_gen:
            number_of_statements_per_gen.remove("")
        if "\n" in number_of_statements_per_gen:
            number_of_statements_per_gen.remove("\n")
        for i in range(len(number_of_statements_per_gen)):
            number_of_statements_per_gen[i] = float(number_of_statements_per_gen[i])
        counts.append(number_of_statements_per_gen)
    # print(f"-------------------- {path} --------------------")

    stats = []
    for gen, count in enumerate(counts):
        # print(f"Gen: {gen:<10} Range: {np.ptp(count):<25} Std: {np.std(count):<25} Mean: {np.mean(count):<25}")
        stats.append([gen, np.ptp(count), np.std(count), np.mean(count)])
    return stats


def average_repeats(all_reps_stats):
    for i in range(len(all_reps_stats)):
        all_reps_stats[i] = np.array(all_reps_stats[i])
    return np.average(all_reps_stats, axis=0).tolist()


def analyze_run(directory):
    files = os.listdir(os.path.join(directory, "Stat"))
    paths = [os.path.join(directory, "Stat", file) for file in files]
    all_reps_stats = []
    for path in paths:
        stats = analyze_stats(path)
        all_reps_stats.append(stats)

    avg_repeats = average_repeats(all_reps_stats)
    return pd.DataFrame(avg_repeats)


def analyze_experiment(path):
    labels = ["LGP", "SGP sm20", "SGP sm40", "SGP sm60"]
    runs = os.listdir(path)
    dfs = {}
    for run in runs:
        if run == "DIV":
            continue
        run = os.path.join(path, run)
        df = analyze_run(run)
        columns = {0: "gen", 1: "range", 2: "std", 3: "mean"}
        df = df.rename(columns=columns)
        dfs[run] = df
    print(dfs)
    index = 0
    for exp, df in dfs.items():
        plt.plot(df['gen'], df['mean'], label=f'{labels[index]}')
        index += 1
    plt.xlabel('Generation')
    plt.ylabel('Mean')
    plt.title("Comparison of mean number of \nexecuted statements by programs over generation")
    plt.legend()
    plt.show()


path = "../diversity_results/"

analyze_experiment(path)

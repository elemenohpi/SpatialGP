import os
import numpy as np


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
    print(f"-------------------- {path} --------------------")
    for gen, count in enumerate(counts):
        print(f"Gen: {gen:<3} Range: {np.ptp(count):<10} Std: {np.std(count):<25} Mean: {np.mean(count):<25} "
              f"Variance: {np.var(count):<25}")


paths = ["../Output/stats.csv", "../Output/stats_lgp.csv"]
for path in paths:
    analyze_stats(path)

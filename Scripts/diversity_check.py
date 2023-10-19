import numpy as np
import scipy.stats as stats
import os

from matplotlib import pyplot as plt


def diversity(path):
    with open(path, "r") as file:
        freq_list = []
        for line in file.readlines():
            fitness_list = line.replace(" ", '').replace("\n", "").split(",")
            del (fitness_list[-1])
            freq = len(set(fitness_list))
            # print(freq, end=" ")
            freq_list.append(freq)
            # print(fitness_list)
        # print("")
    return freq_list


def mean_CI(data):
    # 1. Compute the mean values for each index:
    means = np.mean(data, axis=0)

    # 2. Compute the 95% confidence interval for each index:
    confidence_level = 0.95
    degrees_freedom = len(data) - 1
    confidence_intervals = []
    for i in range(len(means)):
        column_data = [row[i] for row in data]
        std_err = stats.sem(column_data)
        ci = std_err * stats.t.ppf((1 + confidence_level) / 2, degrees_freedom)
        confidence_intervals.append((means[i] - ci, means[i] + ci))

    return means, confidence_intervals


def plot(data):
    # Plotting each set of means and confidence intervals
    for means, cis in data:
        lower, upper = extract_bounds(cis)
        # The y-error for each point is a length-2 tuple: (distance below the point, distance above the point)
        yerr = [[mean - l for mean, l in zip(means, lower)], [u - mean for mean, u in zip(means, upper)]]
        plt.errorbar(range(len(means)), means, yerr=yerr, capsize=5, marker='o', linestyle='-')

    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Comparison of average frequency of unique fitness values')
    plt.legend(['LGP', 'SGP sm20', 'SGP sm40', 'SGP sm60'])  # Adjust this based on the number of datasets you have
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()


# Extracting the lower and upper bounds for each confidence interval
def extract_bounds(cis):
    lower_bounds = [ci[0] for ci in cis]
    upper_bounds = [ci[1] for ci in cis]
    return lower_bounds, upper_bounds


def analyze_experiment(path):
    all_runs = os.listdir(path)
    exp_data = []
    for run in all_runs:
        if run == "DIV":
            continue
        run_path = os.path.join(path, run, "Div")
        files = os.listdir(run_path)
        div_list = []

        for div_file in files:
            div_list.append(diversity(os.path.join(run_path, div_file)))

        means, CIs = mean_CI(div_list)
        exp_data.append([means, CIs])

        print(f"average frequencies of different fitness values for {run}:\n{means}. \nCummalitive Avg: {sum(means)/len(means)}")
    plot(exp_data)


exp_path = "../diversity_results/"
analyze_experiment(exp_path)

#
# for rep in div_1:
#     # print(rep)
#     for index, gen_value in enumerate(rep):
#         sums1[index] += gen_value
#
# avgs1 = [x / len(div_2) for x in sums1]
#
# sums2 = [0] * len(div_2[0])
# for rep in div_2:
#     # print(rep)
#     for index, gen_value in enumerate(rep):
#         sums2[index] += gen_value
#
# avgs2 = [x / len(div_2) for x in sums2]
#
#
# print(f"average frequencies of different fitness values for LGP:\n{avgs1}")
# print(f"average frequencies of different fitness values for SGP:\n{avgs2}")









# ==============================================================
# t_stat, p_value = stats.ttest_ind(avgs1, avgs2)
#
# alpha = 0.05  # Choose your significance level
#
# if p_value < alpha:
#     print("Reject the null hypothesis: There is a significant difference in diversity.")
# else:
#     print("Fail to reject the null hypothesis: There is no significant difference in diversity.")

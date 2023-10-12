import scipy.stats as stats

# a = [19, 24, 26, 20, 16, 19, 25, 22, 15, 21]
# b = [14, 15, 17, 18, 14, 14, 16, 11, 15, 15]
#

#
# print(t_stat, p_value)
#

import os


def diversity(path):
    with open(path, "r") as file:
        freq_list = []
        for line in file.readlines():
            fitness_list = line.replace(" ", '').replace("\n", "").split(",")
            del (fitness_list[-1])
            freq = len(set(fitness_list))
            freq += fitness_list.count('10') - 1
            # print(freq, end=" ")
            freq_list.append(freq)
            # print(fitness_list)
        # print("")
    return freq_list


dir1 = "../diversity_results/rmse_div_lgp/Div/"
dir2 = "../diversity_results/sgp_diversity_second/Div/"

files1 = os.listdir(dir1)
files2 = os.listdir(dir2)

div_1 = []
for file in files1:
    div_1.append(diversity(os.path.join(dir1, file)))

div_2 = []
for file in files2:
    div_2.append(diversity(os.path.join(dir2, file)))

# for rep in div_2:
#     print(rep)
# exit()

sums1 = [0] * len(div_1[0])

for rep in div_1:
    # print(rep)
    for index, gen_value in enumerate(rep):
        sums1[index] += gen_value

avgs1 = [x / len(div_2) for x in sums1]

sums2 = [0] * len(div_2[0])
for rep in div_2:
    # print(rep)
    for index, gen_value in enumerate(rep):
        sums2[index] += gen_value

avgs2 = [x / len(div_2) for x in sums2]


print(f"average frequencies of different fitness values for LGP:\n{avgs1}")
print(f"average frequencies of different fitness values for SGP:\n{avgs2}")

t_stat, p_value = stats.ttest_ind(avgs1, avgs2)

alpha = 0.05  # Choose your significance level

if p_value < alpha:
    print("Reject the null hypothesis: There is a significant difference in diversity.")
else:
    print("Fail to reject the null hypothesis: There is no significant difference in diversity.")

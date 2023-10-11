import scipy.stats as stats

a = [19, 24, 26, 20, 16, 19, 25, 22, 15, 21]
b = [14, 15, 17, 18, 14, 14, 16, 11, 15, 15]

t_stat, p_value = stats.ttest_ind(a, b)

print(t_stat, p_value)

alpha = 0.05  # Choose your significance level

if p_value < alpha:
    print("Reject the null hypothesis: There is a significant difference in diversity.")
else:
    print("Fail to reject the null hypothesis: There is no significant difference in diversity.")
#
# with open("../Output/diversity.csv") as file:
#     for line in file.readlines():
#         fitness_list = line.replace(" ", '').replace("\n", "").split(",")
#         del(fitness_list[-1])
#         freq = len(set(fitness_list))
#         print(freq, end=" ")
#

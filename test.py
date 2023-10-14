import numpy as np

a = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
b = [[3, 3, 3], [2, 2, 2], [1, 1, 1]]

array1 = np.array(a)
array2 = np.array(b)

all = [array1, array2]

average = np.average(all, axis=0)

average = average.tolist()

print(average)

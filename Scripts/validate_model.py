import math
import pickle
import sys

import numpy as np
from scipy import stats

from Handlers.DataHandler import DataHandler

path = "../Output/Population/model_0.sgp"
evaluation_count = 50

evaluation_method = "correlation"

pickled_object = open(path, "rb")
model_object = pickle.load(pickled_object)

fitness_object = model_object.fitness_obj

print(model_object.rmse)
exit()

data_handler = DataHandler("example_data.txt", fitness_object)

data_handler.reset()
sum_error_squared = 0
predicted_results = []
measured_results = []
for i in range(evaluation_count):
    theta = data_handler.get_data(1)
    pi = math.pi
    inputs = [theta, pi]
    print(inputs)
    measured = math.exp(-1 * theta * theta / 2) / math.sqrt(2 * pi)
    measured_results.append(measured)
    try:
        output = model_object.evaluate(inputs)
        predicted_results.append(output)
        error_squared = (measured - output) ** 2
    except OverflowError:
        error_squared = sys.float_info.max
    sum_error_squared += error_squared
if evaluation_method == "rmse":
    rmse = math.sqrt(sum_error_squared / evaluation_count)

elif evaluation_method == "correlation":
    if len(set(predicted_results)) <= 1 or len(predicted_results) != len(measured_results):
        print(10)
    r = np.corrcoef(measured_results, predicted_results)[0, 1]
    pearsonr = stats.pearsonr(predicted_results, measured_results)
    if math.isnan(r):
        print(10)
    print(1 - r ** 2, pearsonr)
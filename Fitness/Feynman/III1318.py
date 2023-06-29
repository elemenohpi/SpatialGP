
import math
import sys
import numpy as np
import warnings
from scipy import stats

from Fitness.AbstractFitness import AbstractFitness
from Handlers.DataHandler import DataHandler

# Suppress all warnings
warnings.filterwarnings("ignore")


class III1318(AbstractFitness):

    def __init__(self) -> None:
        super().__init__()
        self.evaluation_method = "correlation"  # or rmse
        self.evaluation_count = 10
        self.data_handler = DataHandler("Fitness/Feynman/example_data.txt", self)

    def settings(self):
        return {
            "optimization_goal": "min",
        }

    def inputs(self):
        return {
            "h": "float",
            "E": "float",
            "d": "float",
            "k": "float",

        }

    def outputs(self):
        return {
            "v": "float"
        }

    def evaluate(self, individual):
        self.data_handler.reset()
        sum_error_squared = 0
        predicted_results = []
        measured_results = []
        for i in range(self.evaluation_count):
            # ======================================STARTPROBLEM===============================================
            h = self.data_handler.get_data(1)
            E = self.data_handler.get_data(1)
            d = self.data_handler.get_data(1)
            k = self.data_handler.get_data(1)

            inputs = [h, E, d, k]

            measured = 2 * E * d ** 2 * k / h
            # ======================================ENDPROBLEM===============================================
            measured_results.append(measured)
            try:
                output = individual.evaluate(inputs)
                predicted_results.append(output)
                error_squared = (measured - output) ** 2
            except OverflowError:
                error_squared = sys.float_info.max
            sum_error_squared += error_squared
        rmse = math.sqrt(sum_error_squared / self.evaluation_count)
        if self.evaluation_method == "rmse":
            return rmse
        elif self.evaluation_method == "correlation":
            if len(set(predicted_results)) <= 1 or len(predicted_results) != len(measured_results):
                return 10
            try:
                r = stats.pearsonr(measured_results, predicted_results)[0]
            except ValueError:
                return 10
            if math.isnan(r):
                return 10
            try:
                align = np.polyfit(predicted_results, measured_results, 1)
            except BaseException:
                align = [0, 0]

            sum_error_squared = 0
            for index, prediction in enumerate(predicted_results):
                prediction = prediction * align[0] + align[1]
                error_squared = (measured_results[index] - prediction) ** 2
                sum_error_squared += error_squared
            individual.rmse = math.sqrt(sum_error_squared / self.evaluation_count)
            return 1 - r ** 2

    
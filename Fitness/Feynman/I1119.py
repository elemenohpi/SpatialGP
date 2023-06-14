import math
import sys

from Fitness.AbstractFitness import AbstractFitness
from Handlers.DataHandler import DataHandler


class I1119(AbstractFitness):

    def __init__(self) -> None:
        super().__init__()
        self.evaluation_count = 10
        self.data_handler = DataHandler("Fitness/Feynman/example_data.txt", self)

    def settings(self):
        return {
            "optimization_goal": "min",
        }

    def inputs(self):
        return {
            "x[3]": "float",
            "y[3]": "float"
        }

    def outputs(self):
        return {
            "A": "float"
        }

    def evaluate(self, individual):
        self.data_handler.reset()
        sum_error_squared = 0
        for i in range(self.evaluation_count):
            x = self.data_handler.get_data(3)
            y = self.data_handler.get_data(3)
            measured = x[0] * y[0] + x[1] * y[1] + x[2] * y[2]
            inputs = [x, y]
            try:
                output = individual.evaluate(inputs)
                error_squared = (measured - output) ** 2
            except OverflowError:
                error_squared = sys.float_info.max
            sum_error_squared += error_squared
        rmse = math.sqrt(sum_error_squared / self.evaluation_count)
        return rmse

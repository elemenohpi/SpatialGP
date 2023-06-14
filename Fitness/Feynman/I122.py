import math
import sys

from Fitness.AbstractFitness import AbstractFitness
from Handlers.DataHandler import DataHandler


class I122(AbstractFitness):

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
            "q[2]": "float",
            "e": "float",
            "r": "float",
            "pi": "float"
        }

    def outputs(self):
        return {
            "F": "float"
        }

    def evaluate(self, individual):
        self.data_handler.reset()
        sum_error_squared = 0
        for i in range(self.evaluation_count):
            q = self.data_handler.get_data(2)
            e = self.data_handler.get_data(1)
            r = self.data_handler.get_data(1)
            pi = math.pi
            measured = q[0] * q[1] / (4 * pi * e * r * r)
            inputs = [q, e, r, pi]
            try:
                output = individual.evaluate(inputs)
                error_squared = (measured - output) ** 2
            except OverflowError:
                error_squared = sys.float_info.max
            sum_error_squared += error_squared
        rmse = math.sqrt(sum_error_squared / self.evaluation_count)
        return rmse

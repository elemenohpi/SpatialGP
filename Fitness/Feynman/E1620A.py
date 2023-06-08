import math
import sys

from Fitness.AbstractFitness import AbstractFitness
from Handlers.DataHandler import DataHandler


class E1620A(AbstractFitness):

    def __init__(self) -> None:
        super().__init__()
        self.evaluation_count = 10

    def settings(self):
        return {
            "optimization_goal": "min",
        }

    def inputs(self):
        return {
            "theta": "float",
        }

    def outputs(self):
        return {
            "f": "float"
        }

    def evaluate(self, individual):
        data_handler = DataHandler("Fitness/Feynman/example_data.txt")
        sum_error_squared = 0
        for i in range(self.evaluation_count):
            inputs = data_handler.get_data(1)
            theta = inputs[0]
            pi = 3.14
            measured = math.exp(-1 * theta * theta / 2) / math.sqrt(2 * pi)
            try:
                output = individual.evaluate(inputs)
                error_squared = (measured - output) ** 2
            except OverflowError:
                error_squared = sys.float_info.max
            sum_error_squared += error_squared
        rmse = math.sqrt(sum_error_squared / self.evaluation_count)
        return rmse

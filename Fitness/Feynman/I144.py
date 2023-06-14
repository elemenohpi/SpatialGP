import math
import sys

from Fitness.AbstractFitness import AbstractFitness
from Handlers.DataHandler import DataHandler


class I144(AbstractFitness):

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
            "k": "float",
            "x": "float"
        }

    def outputs(self):
        return {
            "U": "float"
        }

    def evaluate(self, individual):
        self.data_handler.reset()
        sum_error_squared = 0
        for i in range(self.evaluation_count):
            k = self.data_handler.get_data(1)
            x = self.data_handler.get_data(1)
            measured = k * x * x / 2
            inputs = [k, x]
            try:
                output = individual.evaluate(inputs)
                error_squared = (measured - output) ** 2

            except OverflowError:
                error_squared = sys.float_info.max
            sum_error_squared += error_squared
        rmse = math.sqrt(sum_error_squared / self.evaluation_count)
        return rmse

import random
import math
from Fitness.AbstractFitness import AbstractFitness
from scipy import stats
import numpy as np


class E9(AbstractFitness):

    def __init__(self) -> None:
        super().__init__()

    def settings(self):
        return {
            "optimization_goal": "min"
        }

    def inputs(self):
        return {
            "x[2]": "float"
        }

    def outputs(self):
        return {
            "fx12": "float"
        }

    def evaluate(self, individual):
        d1 = [1, 5, 3, 6, 10]
        d2 = [3, 6, 3, 4, 2]
        sum_error_squared = 0
        for i in range(len(d1)):
            x1 = d1[i]
            x2 = d2[i]
            inputs = [[x1, x2]]
            measured = x1 ** 4 - x1 ** 3 + x2 ** 2 / 2 - x2
            output = individual.evaluate(inputs)
            error_squared = (measured - output) ** 2
            sum_error_squared += error_squared
        rmse = math.sqrt(sum_error_squared / len(d1))
        return rmse

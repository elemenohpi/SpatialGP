import random
import math
from Fitness.AbstractFitness import AbstractFitness
from scipy import stats
import numpy as np


class E12(AbstractFitness):

    def __init__(self) -> None:
        super().__init__()

    def settings(self):
        return {
            "optimization_goal": "min"
        }

    def inputs(self):
        return {
            "x[10]": "float"
        }

    def outputs(self):
        return {
            "fx12": "float"
        }

    def evaluate(self, individual):
        d1 = [1, 5, 3, 6, 10]
        d2 = [3, 6, 3, 4, 2]
        d3 = [2, 1, 6, 9, 1]
        d4 = [5, 2, 7, 8, 9]
        d5 = [1, 1, 4, 7, 8]
        d6 = [6, 6, 7, 5, 2]
        d7 = [5, 3, 2, 1, 9]
        d8 = [1, 9, 9, 9, 2]
        d9 = [3, 2, 3, 4, 4]
        d10 = [1, 5, 5, 6, 3]
        sum_error_squared = 0
        for i in range(len(d1)):
            x1 = d1[i]
            x2 = d2[i]
            x3 = d3[i]
            x4 = d4[i]
            x5 = d5[i]
            x6 = d6[i]
            x7 = d7[i]
            x8 = d8[i]
            x9 = d9[i]
            x10 = d10[i]
            inputs = [[x1, x2, x3, x4, x5, x6, x7, x8, x9, x10]]
            measured = x1 * x2 + x3 * x4 + x5 * x6 + x1 * x7 * x9 + x3 * x6 * x10
            output = individual.evaluate(inputs)
            error_squared = (measured - output) ** 2
            sum_error_squared += error_squared
        rmse = math.sqrt(sum_error_squared / len(d1))
        return rmse

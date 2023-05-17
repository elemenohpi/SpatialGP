import random
import math

from Fitness.AbstractFitness import AbstractFitness


class SimpleProblem(AbstractFitness):
    def inputs(self):
        return {
            "radius": "float",
            "pi": "float"
        }

    def outputs(self):
        return {
            "surface": "float"
        }

    def preprocess(self, indv):
        pass

    def evaluate(self, indv):
        a = [1, 5, 10, 15, 20]
        pi = math.pi
        sum_error_squared = 0
        for radius in a:
            inputs = [radius, pi]
            measured_surface = pi * radius ** 2
            model_fitness = indv.evaluate(inputs)
            if model_fitness is None:
                return
            error_squared = (measured_surface - model_fitness) ** 2
            sum_error_squared += error_squared
        rmse = math.sqrt(sum_error_squared/len(a))
        return rmse

    def postprocess(self, indv):
        pass

import math
import sys
import numpy as np
import warnings
from scipy import stats

from Fitness.AbstractFitness import AbstractFitness
from Handlers.UsefulDataHandler import UsefulDataHandler

# Suppress all warnings
warnings.filterwarnings("ignore")


class PIController(AbstractFitness):

    def __init__(self) -> None:
        super().__init__()
        self.data_handler = UsefulDataHandler()
        self.data_handler.read_data("D:\Projects\SGP\SpatialGP\Fitness\ControlProblem\data.csv")

    def settings(self):
        return {
            "optimization_goal": "min",
        }

    def inputs(self):
        return {
            "vc0": "float",
            "uc0": "float",
            "uc": "float",
            "uh": "float",
            "up": "float",
            "Vc": "float",
            "Tco": "float",
            "Thi": "float"
        }

    def outputs(self):
        return {
            "Kc": "float",
            "Ti": "float",
        }

    def evaluate(self, individual):
        # Set points
        r_Vc = 200
        r_Tco = 40
        r_Thi = 50

        Ts = 1

        error = 0
        self.data_handler.reset()
        inputs = self.data_handler.get_data()
        [uc0, uh0, up0, Vc0, Tco0, Thi0] = inputs
        for i in range(self.data_handler.get_length()-2):
            inputs = self.data_handler.get_data()
            [uc, uh, up, Vc, Tco, Thi] = inputs
            try:
                output = individual.evaluate([uc0, Vc0] + inputs)
                [Kc, Ti] = output
                if Ti == 0:
                    Ti = 0.01
            except OverflowError:
                Kc, Ti = 1000, 10000

            error += abs(uc0 + Kc * ((1 + Ts / Ti) * (r_Vc - Vc) - (r_Vc - Vc0)) - uc)
            # error += abs(uh0 + Kc * ((1 + Ts / Ti) * (r_Tco - Vc) - (r_Tco - Tco0)) - uh)
            # error += abs(up0 + Kc * ((1 + Ts / Ti) * (r_Thi - Vc) - (r_Thi - Thi0)) - up)

            [uc0, uh0, up0, Vc0, Tco0, Thi0] = [uc, uh, up, Vc, Tco, Thi]
        print("Error: ", error)
        return error


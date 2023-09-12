from Fitness.AbstractFitness import AbstractFitness
from lib.WaterSortPuzzleLib import WaterPuzzle


class WaterSortPuzzle(AbstractFitness):
    def __init__(self):
        super().__init__()
        pass

    def inputs(self):
        return {
            "m0": "float"
        }

    def outputs(self):
        return {
            "m": "float"
        }

    def settings(self):
        return {
            "optimization_goal": "max",
        }

    def evaluate(self, indv):
        wp = WaterPuzzle(6)


        return 0





from Fitness.AbstractFitness import AbstractFitness
from Fitness.libs.ObstacleAvoidance import ObstacleAvoidance


class ObstacleAvoidanceProblem(AbstractFitness):

    def __init__(self) -> None:
        super().__init__()
        self.task = ObstacleAvoidance()

    def settings(self):
        return {
            "optimization_goal": "max",
        }

    def inputs(self):
        return {
            "x0": "int",
            "x1": "int",
            "x2": "int",
            "x3": "int",
            "x4": "int",
            "x5": "int",
            "x6": "int",
            "x7": "int",
            "x8": "int",
            "x9": "int",
            "x10": "int",
            "x11": "int",
        }

    def outputs(self):
        return [0, 1, 2]  # Left, Right, NoAction

    def evaluate(self, individual):
        fitness = 0
        for _ in range(5):
            obs, done, reward = self.task.reset()
            for _ in range(100):
                input_list = [
                    obs[0],
                    obs[1],
                    obs[2],
                    obs[3],
                    obs[4],
                    obs[5],
                    obs[6],
                    obs[7],
                    obs[8],
                    obs[3],
                    obs[4],
                    obs[5],
                ]

                output = individual.evaluate(input_list)
                if not output:
                    output = 0

                action = int(output)

                obs, done, reward = self.task.step(action)

                if done:
                    break
            fitness += reward
        return fitness / 5

from Fitness.AbstractFitness import AbstractFitness
from Fitness.lib.ObstacleAvoidance import ObstacleAvoidance


class ObstacleAvoidanceProblem(AbstractFitness):

    def __init__(self) -> None:
        super().__init__()
        # 0 is empty space, 1 is obstacle, 2 is treasure, 3 is agent facing north, 4 is agent facing east,
        # 5 is agent facing south, 6 is agent facing west, 7 is end tile, 8 is a trap
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
        return [0, 1, 2]

    def evaluate(self, individual):
        fitness = 0

        for _ in range(5):
            obs, done, reward = self.task.reset()
            for _ in range(100):
                input_dict = [
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

                output = individual.evaluate(input_dict)
                if not output:
                    output = 0

                action = int(output)

                obs, done, reward = self.task.step(action)
                # if individual.individual_index == 0:
                # 	print("action", action)
                # 	self.task.show_map()
                # 	print("reward", reward)

                if done:
                    break
            fitness += reward
        # print("reward: ", reward, individual.individual_index)
        # print("==================")
        return fitness / 5

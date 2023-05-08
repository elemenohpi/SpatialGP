from Fitness.AbstractFitness import AbstractFitness


class EmptyProblem(AbstractFitness):
    def preprocess(self, indv):
        pass

    def evaluate(self, indv):
        return 0

    def postprocess(self, indv):
        pass
